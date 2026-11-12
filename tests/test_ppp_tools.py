"""Requirement-based checks for the portable tools.

Expected results come from the attached design's provenance, actual-duration,
separate-evidence, independent-practice, and caption integrity requirements.
Small fixtures contain no real learner data or copied video frames.
"""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ppp_tools.py"
SPEC = importlib.util.spec_from_file_location("ppp_tools", SCRIPT)
tools = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tools)


def session():
    return {
        "schema_version": 1,
        "kind": "session",
        "date": "2026-11-09",
        "topic": "Derivative versus stationary point",
        "goals": ["Distinguish stationary point from an extremum"],
        "events": [{
            "problem_id": "generated-cubic-1",
            "provenance": "generated",
            "source": None,
            "assistance": "none",
            "outcome": "correct",
            "evidence": "Learner found f'(x)=3x² and showed increasing values on both sides of zero.",
            "attribution": "observed-work",
            "transfer": True,
            "independent_success": True,
        }],
        "next_step": "Try a different function without hints.",
        "duration": {"seconds": None, "basis": "unknown"},
    }


def visual():
    return {
        "schema_version": 1,
        "kind": "visual-evidence",
        "source": {"title": "Test source", "creator": "Fixture", "url": "https://example.org/fixture"},
        "captured_at": "2026-11-09T12:00:00-05:00",
        "visual_status": "incomplete",
        "frames": [],
        "observations": [],
        "transcript_claims": ["This is a fixture, not an inspected video."],
        "interpretations": [],
    }


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.parent = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def errors(self, value):
        return tools.validate_record(value, self.parent)

    def test_unknown_duration_does_not_invent_minutes(self):
        self.assertEqual(self.errors(session()), [])
        record = session()
        record["duration"]["seconds"] = 600
        self.assertTrue(any("must be null" in error for error in self.errors(record)))

    def test_actual_duration_uses_timezone_aware_elapsed_seconds(self):
        record = session()
        record["duration"] = {"basis": "measured", "seconds": 75.5, "start": "2026-11-09T12:00:00-05:00", "end": "2026-11-09T17:01:15.5Z"}
        self.assertEqual(self.errors(record), [])
        record["duration"]["seconds"] = 75
        self.assertTrue(any("expected 75.5" in error for error in self.errors(record)))
        record["duration"]["start"] = "2026-11-09T12:00:00"
        self.assertTrue(any("timezone" in error for error in self.errors(record)))

    def test_assisted_recognition_is_not_independent_success(self):
        for key, value in (("assistance", "full-solution"), ("attribution", "learner-statement"), ("outcome", "partial"), ("evidence", "")):
            with self.subTest(key=key):
                record = session()
                record["events"][0][key] = value
                self.assertTrue(any("independent_success" in error for error in self.errors(record)))

    def test_past_paper_requires_source_locator(self):
        record = session()
        record["events"][0]["provenance"] = "past-paper"
        self.assertTrue(any("source locator" in error for error in self.errors(record)))
        record["events"][0]["source"] = "course/exam-2024.pdf, Q3"
        self.assertEqual(self.errors(record), [])

    def test_invalid_types_report_errors_instead_of_crashing(self):
        for key, value in (("schema_version", True), ("events", None), ("duration", []), ("date", "2026-02-31"), ("goals", "understand")):
            with self.subTest(key=key):
                record = session()
                record[key] = value
                self.assertTrue(self.errors(record))
        for value in (True, float("nan"), float("inf"), -1, "20", 10**1000):
            with self.subTest(seconds=value):
                record = session()
                record["duration"] = {"basis": "user-estimate", "seconds": value}
                self.assertTrue(self.errors(record))
        self.assertTrue(self.errors([]))

    def test_missing_fields_and_non_boolean_flags_are_rejected(self):
        record = session()
        del record["duration"]["seconds"]
        record["events"][0]["transfer"] = 1
        record["events"].append(None)
        self.assertGreaterEqual(len(self.errors(record)), 3)

    def test_incomplete_visual_research_is_honestly_representable(self):
        self.assertEqual(self.errors(visual()), [])
        record = visual()
        record["visual_status"] = "complete"
        self.assertTrue(any("absent visual evidence" in error for error in self.errors(record)))

    def frames(self):
        frames = []
        for number in (1, 2):
            name = f"frame-{number}.png"
            (self.parent / name).write_bytes(b"fixture, not a genuine screenshot")
            frames.append({"file": name, "timestamp_seconds": number, "visible_timestamp": f"0:0{number}", "inspected": True})
        return frames

    def test_motion_needs_ordered_inspected_frames(self):
        record = visual()
        record.update(visual_status="complete", frames=self.frames(), motion_claim={"basis": "ordered-frames", "evidence": "Fixture sequence for structural testing only."})
        self.assertEqual(self.errors(record), [])
        for mutation in ("reverse", "duplicate", "uninspected", "single"):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(record)
                if mutation == "reverse":
                    changed["frames"].reverse()
                elif mutation == "duplicate":
                    changed["frames"][1]["timestamp_seconds"] = 1
                elif mutation == "uninspected":
                    changed["frames"][0]["inspected"] = False
                else:
                    changed["frames"] = changed["frames"][:1]
                self.assertTrue(any("ordered-frames" in error for error in self.errors(changed)))

    def test_frame_paths_exist_and_cannot_escape_record_directory(self):
        record = visual()
        record["frames"] = self.frames()
        for path in ("missing.png", "../outside.png", str(self.parent / "frame-1.png")):
            with self.subTest(path=path):
                record["frames"][0]["file"] = path
                self.assertTrue(any("frames[0].file" in error for error in self.errors(record)))

    def test_visual_malformed_values_report_errors(self):
        for key, value in (("source", []), ("captured_at", "yesterday"), ("observations", {}), ("frames", True), ("motion_claim", "motion")):
            with self.subTest(key=key):
                record = visual()
                record[key] = value
                self.assertTrue(self.errors(record))
        record = visual()
        record["source"]["url"] = "javascript:alert(1)"
        record["frames"] = [{"file": "missing", "timestamp_seconds": True, "visible_timestamp": None, "inspected": 1}]
        self.assertGreaterEqual(len(self.errors(record)), 5)

    def test_strict_json_rejects_nan_and_duplicate_fields(self):
        file = self.parent / "record.json"
        for raw in ('{"seconds": NaN}', '{"kind": "session", "kind": "visual-evidence"}'):
            with self.subTest(raw=raw):
                file.write_text(raw, encoding="utf-8")
                with self.assertRaises(ValueError):
                    tools.read_json(file)


class CaptionTests(unittest.TestCase):
    def test_valid_multiline_bom_crlf_captions(self):
        text = "\ufeff1\r\n00:00:00,000 --> 00:00:02,500\r\nPredict first.\r\nThen reveal.\r\n\r\n2\r\n00:00:02,500 --> 00:00:04,000\r\nExplain your reasoning.\r\n"
        self.assertEqual(tools.check_captions(text, 4), ([], 2))

    def test_bad_syntax_cannot_silently_drop_a_cue(self):
        cases = (
            "1\n00:00:00,000 --> 00:00:01,000\nGood\n\n2\nnot timing\nHidden",
            "1\n00:00:00.000 --> 00:00:01.000\nWrong decimal separator",
            "1\n00:60:00,000 --> 01:00:01,000\nInvalid minutes",
            "1\n00:00:60,000 --> 00:01:01,000\nInvalid seconds",
            "2\n00:00:00,000 --> 00:00:01,000\nWrong cue index",
            "1\n00:00:00,000 --> 00:00:01,000",
            "",
        )
        for text in cases:
            with self.subTest(text=text):
                self.assertTrue(tools.check_captions(text, 5000)[0])

    def test_overlap_zero_span_reversed_and_overrun_fail(self):
        for text in (
            "1\n00:00:00,000 --> 00:00:02,000\nA\n\n2\n00:00:01,999 --> 00:00:03,000\nB",
            "1\n00:00:01,000 --> 00:00:01,000\nA",
            "1\n00:00:02,000 --> 00:00:01,000\nA",
            "1\n00:00:00,000 --> 00:00:04,051\nA",
        ):
            with self.subTest(text=text):
                self.assertTrue(tools.check_captions(text, 4)[0])
        self.assertFalse(tools.check_captions("1\n00:00:00,000 --> 00:00:04,050\nA", 4)[0])

    def test_nonfinite_or_nonpositive_duration_fails(self):
        for duration in (float("nan"), float("inf"), -1, 0, True):
            self.assertTrue(tools.check_captions("1\n00:00:00,000 --> 00:00:01,000\nA", duration)[0])


class RuntimeTests(unittest.TestCase):
    def test_audit_makes_no_functional_claim(self):
        with patch.object(tools.subprocess, "run", side_effect=AssertionError("audit must not run external tools")):
            result = tools.audit()
        self.assertEqual(result["functional_verification"], "not-run")
        self.assertEqual(result["python"]["executable"], sys.executable)
        self.assertIn("manim", result["packages"])
        self.assertIn("manimgl", result["packages"])

    def test_missing_media_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(tools.media_info(Path(temp) / "missing.mp4", 1)["status"], "invalid")

    def test_media_unavailable_and_decode_failure_are_distinct(self):
        with tempfile.TemporaryDirectory() as temp:
            media = Path(temp) / "fake.mp4"
            media.write_bytes(b"fixture")
            with patch.object(tools.shutil, "which", return_value=None):
                self.assertEqual(tools.media_info(media, 1)["status"], "unavailable")
            returns = [
                {"returncode": 0, "stdout": '{"streams": [{"codec_type": "audio"}]}', "stderr": "", "timed_out": False},
                {"returncode": 1, "stdout": "", "stderr": "invalid frame", "timed_out": False},
            ]
            with patch.object(tools.shutil, "which", side_effect=lambda value: value), patch.object(tools, "bounded_process", side_effect=returns):
                result = tools.media_info(media, 1)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(result["audio_present"])
            self.assertEqual(result["perceptual_review"], "not-run")

    def test_malformed_probe_json_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            media = Path(temp) / "fake.mp4"
            media.write_bytes(b"fixture")
            for raw in ("[]", "invalid JSON", '{"streams": []}'):
                with self.subTest(raw=raw):
                    result = {"returncode": 0, "stdout": raw, "stderr": "", "timed_out": False}
                    with patch.object(tools.shutil, "which", side_effect=lambda value: value), patch.object(tools, "bounded_process", return_value=result):
                        self.assertEqual(tools.media_info(media, 1)["status"], "invalid")

    def test_required_streams_follow_the_selected_delivery_contract(self):
        """Narrated delivery requires audio; silent previews remain valid by default."""
        with tempfile.TemporaryDirectory() as temp:
            media = Path(temp) / "fake.mp4"
            media.write_bytes(b"fixture")
            cases = (
                (["video"], False, False, "passed", []),
                (["video"], True, True, "failed", ["media: required audio stream is absent"]),
                (["audio"], False, True, "failed", ["media: required video stream is absent"]),
                (["audio", "video"], True, True, "passed", []),
            )
            for stream_types, require_audio, require_video, expected_status, expected_errors in cases:
                with self.subTest(stream_types=stream_types, require_audio=require_audio, require_video=require_video):
                    returns = [
                        {"returncode": 0, "stdout": json.dumps({"streams": [{"codec_type": item} for item in stream_types]}), "stderr": "", "timed_out": False},
                        {"returncode": 0, "stdout": "", "stderr": "", "timed_out": False},
                    ]
                    with patch.object(tools.shutil, "which", side_effect=lambda value: value), patch.object(tools, "bounded_process", side_effect=returns):
                        result = tools.media_info(media, 1, require_audio=require_audio, require_video=require_video)
                    self.assertEqual(result["status"], expected_status)
                    self.assertEqual(result["errors"], expected_errors)
                    self.assertEqual(result["audio_present"], "audio" in stream_types)
                    self.assertEqual(result["video_present"], "video" in stream_types)

    def test_cli_required_stream_flags_return_failure_when_contract_fails(self):
        with patch.object(tools, "media_info", return_value={"status": "failed", "errors": ["media: required audio stream is absent"]}) as check, contextlib.redirect_stdout(io.StringIO()):
            result = tools.main(["media-info", "lesson.mp4", "--require-audio", "--require-video", "--timeout", "20"])
        self.assertEqual(result, 1)
        check.assert_called_once_with(Path("lesson.mp4"), 20, require_audio=True, require_video=True)

    def test_process_timeout_is_explicit(self):
        with patch.object(tools.subprocess, "run", side_effect=subprocess.TimeoutExpired(["fixture"], 1)):
            result = tools.bounded_process(["fixture"], 1)
        self.assertTrue(result["timed_out"])
        self.assertIsNone(result["returncode"])

    def test_cli_invalid_record_returns_nonzero_json(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "bad.json"
            file.write_text('{"schema_version":true}', encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = tools.main(["validate-record", str(file)])
            self.assertEqual(result, 1)
            parsed = json.loads(output.getvalue())
            self.assertEqual(parsed["status"], "invalid")
            self.assertIn("not proof", parsed["limitation"])

    def test_cli_missing_record_and_nan_timeout_return_nonzero(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tools.main(["validate-record", str(Path(temp) / "missing.json")]), 1)
            self.assertEqual(tools.main(["media-info", "fixture.mp4", "--timeout", "nan"]), 1)


def bank():
    return {
        "schema_version": 1,
        "kind": "question-bank",
        "items": [
            {
                "problem_id": "generated-cubic-1",
                "provenance": "generated",
                "source": None,
                "concepts": ["stationary point"],
                "exposure": "attempted",
                "protected": False,
                "attempts": [{"date": "2026-11-01", "outcome": "incorrect", "assistance": "hint", "recall": "again"}],
                "next_review": "2026-11-04",
            },
            {
                "problem_id": "exam-2025-q3",
                "provenance": "past-paper",
                "source": "course/exam-2025.pdf, Q3",
                "concepts": [],
                "exposure": "unseen",
                "protected": True,
                "attempts": [],
                "next_review": None,
            },
        ],
    }


class RevisionSevenRecordTests(unittest.TestCase):
    """Synthetic observations exercise assistance, repeated saves and disclosure."""

    def errors(self, record):
        return tools.validate_record(record, Path.cwd())

    def test_honest_unknown_or_ai_help_is_valid_but_never_independent(self):
        for assistance in ("unknown", "ai-assisted"):
            with self.subTest(assistance=assistance):
                record = session()
                event = record["events"][0]
                event.update(assistance=assistance, independent_success=False)
                self.assertEqual(self.errors(record), [])
                event["independent_success"] = True
                self.assertTrue(any("independent_success" in error for error in self.errors(record)))
                review = bank()
                review["items"][0]["attempts"][0]["assistance"] = assistance
                self.assertEqual(self.errors(review), [])

    def test_guess_recognition_or_unknown_basis_cannot_support_independence(self):
        for basis in ("recognition", "guess", "unknown"):
            with self.subTest(basis=basis):
                record = session()
                event = record["events"][0]
                event["response_basis"] = basis
                self.assertTrue(any("independent_success" in error for error in self.errors(record)))
                event["independent_success"] = False
                self.assertEqual(self.errors(record), [])
        record = session()
        record["events"][0]["response_basis"] = "reasoned"
        self.assertEqual(self.errors(record), [])

    def test_invalid_optional_fields_rejected_in_both_record_types(self):
        for record in (session(), bank()):
            event = record["events"][0] if "events" in record else record["items"][0]["attempts"][0]
            for key, value in (("attempt_id", []), ("attempt_id", " "), ("response_basis", []),
                               ("response_basis", "almost-mastered")):
                with self.subTest(kind=record["kind"], key=key, value=value):
                    event[key] = value
                    self.assertTrue(any(key in error for error in self.errors(record)))
                    del event[key]

    def test_replayed_session_id_rejected_and_distinct_same_day_retry_accepted(self):
        record = session()
        event = record["events"][0]
        event["attempt_id"] = "lesson-q1-first"
        record["events"].append(copy.deepcopy(event))
        self.assertTrue(any("attempt_id" in error for error in self.errors(record)))
        record["events"][-1]["attempt_id"] = "lesson-q1-retry"
        self.assertEqual(self.errors(record), [])

    def test_bank_rejects_replayed_id_across_problems_and_accepts_in_place_correction(self):
        record = bank()
        original = record["items"][0]
        attempt = original["attempts"][0]
        attempt["attempt_id"] = "session-q1-a"
        copied = copy.deepcopy(original)
        copied["problem_id"] = "separate-problem"
        record["items"].append(copied)
        self.assertTrue(any("attempt_id" in error for error in self.errors(record)))
        record["items"].pop()
        attempt.update(assistance="unknown", response_basis="guess")
        self.assertEqual(self.errors(record), [])
        self.assertEqual(len(original["attempts"]), 1)

    def test_legacy_v1_needs_no_backfill_and_unsupported_version_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            for record in (session(), bank()):
                path = Path(directory) / "synthetic.json"
                for version, expected_status in ((1, 0), (2, 1)):
                    with self.subTest(kind=record["kind"], version=version):
                        record["schema_version"] = version
                        payload = json.dumps(record).encode()
                        path.write_bytes(payload)
                        with contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(tools.main(["validate-record", str(path)]), expected_status)
                        self.assertEqual(path.read_bytes(), payload)

    def test_brief_due_discloses_only_id_and_date_and_never_rewrites_the_bank(self):
        record = bank()
        record["items"][0]["private_note"] = "SYNTHETIC-PRIVATE-NOTE"
        later = copy.deepcopy(record["items"][0])
        later.update(problem_id="other", next_review="2026-11-08")
        record["items"].insert(0, later)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bank.json"
            payload = json.dumps(record).encode()
            path.write_bytes(payload)
            args = [sys.executable, "-B", str(SCRIPT), "due", str(path), "--on", "2026-11-09"]
            brief = subprocess.run([*args, "--brief"], capture_output=True)
            self.assertEqual(brief.returncode, 0, brief.stderr)
            report = json.loads(brief.stdout)
            self.assertEqual(report["due"], [
                {"problem_id": "generated-cubic-1", "next_review": "2026-11-04"},
                {"problem_id": "other", "next_review": "2026-11-08"},
            ])
            self.assertNotIn(b"SYNTHETIC-PRIVATE-NOTE", brief.stdout + brief.stderr)
            self.assertNotIn(b"exam-2025", brief.stdout + brief.stderr)
            full = subprocess.run(args, capture_output=True, check=True)
            self.assertEqual(json.loads(full.stdout)["due"][0], record["items"][1])
            self.assertEqual(path.read_bytes(), payload)

    def test_invalid_brief_input_cannot_expose_protected_names_or_duplicate_keys(self):
        invalid = bank()
        reserved = invalid["items"][1]
        reserved["problem_id"] = "SYNTHETIC-PRIVATE-ID"
        invalid["items"].append(dict(reserved))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bank.json"
            for raw in (json.dumps(invalid), '{"SYNTHETIC-PRIVATE-KEY":1,"SYNTHETIC-PRIVATE-KEY":2}'):
                with self.subTest(raw=raw):
                    path.write_text(raw, encoding="utf-8")
                    result = subprocess.run([sys.executable, "-B", str(SCRIPT), "due", str(path),
                                             "--brief"], capture_output=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(json.loads(result.stdout)["status"], "invalid")
                    self.assertNotIn(b"SYNTHETIC-PRIVATE", result.stdout + result.stderr)


class RevisionFourRecordTests(unittest.TestCase):
    """Defects reproduced against v3 on 2026-11-09, plus the question bank."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.parent = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def errors(self, value, **options):
        return tools.validate_record(value, self.parent, **options)

    def test_attempted_event_needs_evidence_text(self):
        record = session()
        record["events"][0]["independent_success"] = False
        record["events"][0]["evidence"] = "   "
        self.assertTrue(any("evidence" in error for error in self.errors(record)))
        record["events"][0]["outcome"] = "not-attempted"
        self.assertEqual(self.errors(record), [])

    def test_inquiry_fields_are_null_or_text(self):
        record = session()
        record["inquiry"] = {"question": None, "prediction": "It will loop back.", "observation": None, "open_question": None}
        self.assertEqual(self.errors(record), [])
        for value in (12, "", ["agent wrote this"], {}):
            with self.subTest(value=value):
                record["inquiry"]["question"] = value
                self.assertTrue(any("inquiry.question" in error for error in self.errors(record)))
        record["inquiry"] = "a question"
        self.assertTrue(any("inquiry" in error for error in self.errors(record)))

    def test_template_placeholders_are_not_real_records(self):
        assets = SCRIPT.parents[1] / "assets"
        for name in ("session.template.json", "inquiry-session.template.json", "visual-evidence.template.json", "question-bank.template.json"):
            with self.subTest(name=name):
                record = tools.read_json(assets / name)
                self.assertTrue(any("template" in error.lower() for error in self.errors(record)))
                self.assertEqual(self.errors(record, allow_template=True), [])
        record = session()
        record["topic"] = "Template matching in computer vision"
        record["next_step"] = "Replace with substitution u = x² and retry."
        self.assertEqual(self.errors(record), [])

    def test_session_date_cannot_be_in_the_future(self):
        record = session()
        record["date"] = "2999-01-01"
        self.assertTrue(any("future" in error for error in self.errors(record)))

    def test_unanswered_transfer_prompt_stays_representable(self):
        """A transfer task shown but not attempted is pending, not an error."""
        record = session()
        record["events"][0].update(outcome="not-attempted", independent_success=False, evidence="")
        self.assertEqual(self.errors(record), [])

    def test_question_bank_accepts_reviewable_and_protected_items(self):
        self.assertEqual(self.errors(bank()), [])

    def test_protected_paper_cannot_be_exposed_or_scheduled(self):
        for key, value in (("exposure", "attempted"), ("next_review", "2026-12-01"), ("attempts", [{"date": "2026-11-01", "outcome": "correct", "assistance": "none", "recall": None}])):
            with self.subTest(key=key):
                record = bank()
                record["items"][1][key] = value
                self.assertTrue(any("protected" in error for error in self.errors(record)))

    def test_question_bank_rejects_inconsistent_items(self):
        mutations = (
            ("duplicate id", lambda r: r["items"][1].update(problem_id="generated-cubic-1")),
            ("bad recall", lambda r: r["items"][0]["attempts"][0].update(recall="perfect")),
            ("review before last attempt", lambda r: r["items"][0].update(next_review="2026-10-01")),
            ("attempts out of order", lambda r: r["items"][0]["attempts"].append({"date": "2026-10-01", "outcome": "correct", "assistance": "none", "recall": "good"})),
            ("unseen with attempts", lambda r: r["items"][0].update(exposure="unseen")),
            ("past paper without source", lambda r: r["items"][1].update(source=None)),
            ("items not a list", lambda r: r.update(items={})),
            ("bad concepts", lambda r: r["items"][0].update(concepts="chain rule")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                record = bank()
                mutate(record)
                self.assertTrue(self.errors(record))

    def test_due_lists_only_unprotected_items_on_or_before_the_day(self):
        record = bank()
        record["items"].append({"problem_id": "later", "provenance": "generated", "source": None, "concepts": [], "exposure": "worked", "protected": False, "attempts": [], "next_review": "2026-12-25"})
        self.assertEqual([item["problem_id"] for item in tools.due_items(record, tools.date(2026, 11, 9))], ["generated-cubic-1"])
        self.assertEqual(tools.due_items(record, tools.date(2026, 11, 3)), [])
        self.assertEqual(len(tools.due_items(record, tools.date(2026, 12, 25))), 2)

    def test_cli_due_refuses_an_invalid_bank(self):
        file = self.parent / "bank.json"
        record = bank()
        record["items"][1]["next_review"] = "2026-12-01"
        file.write_text(json.dumps(record), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(tools.main(["due", str(file), "--on", "2026-12-25"]), 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "invalid")
        file.write_text(json.dumps(bank()), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(tools.main(["due", str(file), "--on", "2026-11-09"]), 0)
        parsed = json.loads(output.getvalue())
        self.assertEqual(parsed["due_count"], 1)
        self.assertIn("Nothing was scheduled", parsed["limitation"])


class RevisionFourCaptionTests(unittest.TestCase):
    def test_media_duration_rejects_a_failed_probe_even_with_duration_output(self):
        """A failed external probe cannot certify a duration from partial output."""
        with tempfile.TemporaryDirectory() as temp:
            media = Path(temp) / "fixture.mp4"
            media.write_bytes(b"path-only fixture; the probe result is controlled")
            srt = Path(temp) / "captions.srt"
            srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")
            failures = (
                {"returncode": 1, "stdout": '{"format":{"duration":"2.0"}}',
                 "stderr": "fatal probe error", "timed_out": False},
                {"returncode": None, "stdout": "", "stderr": "Command exceeded 60s timeout",
                 "timed_out": True},
                {"returncode": 2, "stdout": '{"format":{"duration":"2.0"}}',
                 "stderr": "", "timed_out": False},
            )
            for failure in failures:
                with self.subTest(failure=failure), patch.object(tools.shutil, "which", return_value="ffprobe"), \
                        patch.object(tools, "bounded_process", return_value=failure):
                    duration, error = tools.media_duration(media, 60)
                    self.assertIsNone(duration)
                    self.assertIsNotNone(error)
                    self.assertIn(failure["stderr"] or "2", error)
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        code = tools.main(["check-captions", str(srt), "--media", str(media)])
                    self.assertEqual(code, 1)
                    parsed = json.loads(output.getvalue())
                    self.assertEqual(parsed["status"], "invalid")
                    self.assertIn(error, parsed["errors"])

    def test_extra_blank_lines_and_cue_settings_are_tolerated(self):
        text = "1\n00:00:00,000 --> 00:00:01,000 X1:40 X2:600 Y1:20 Y2:50\nHi\n\n\n\n2\n00:00:01,000 --> 00:00:02,000\nYo\n"
        self.assertEqual(tools.check_captions(text, 10), ([], 2))

    def test_webvtt_gets_a_format_error_not_cue_noise(self):
        errors, _ = tools.check_captions("WEBVTT\n\n00:00.000 --> 00:01.000\nHi\n", 10)
        self.assertEqual(len(errors), 1)
        self.assertIn("WebVTT", errors[0])

    def test_cli_needs_exactly_one_duration_source(self):
        with tempfile.TemporaryDirectory() as temp:
            srt = Path(temp) / "c.srt"
            srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nHi\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    tools.main(["check-captions", str(srt)])
                with patch.object(tools, "media_duration", return_value=(0.5, None)):
                    self.assertEqual(tools.main(["check-captions", str(srt), "--media", "lesson.mp4"]), 1)
                with patch.object(tools, "media_duration", return_value=(1.0, None)):
                    self.assertEqual(tools.main(["check-captions", str(srt), "--media", "lesson.mp4"]), 0)
                with patch.object(tools, "media_duration", return_value=(None, "ffprobe missing")):
                    self.assertEqual(tools.main(["check-captions", str(srt), "--media", "lesson.mp4"]), 1)


class RevisionFourRuntimeTests(unittest.TestCase):
    def test_non_ascii_error_survives_a_legacy_console_encoding(self):
        """v3 replaced the real error with a charmap failure on cp1252 pipes."""
        with tempfile.TemporaryDirectory() as temp:
            record = visual()
            record["frames"] = [{"file": "框架.png", "timestamp_seconds": 1, "visible_timestamp": "0:01", "inspected": True}]
            file = Path(temp) / "record.json"
            file.write_text(json.dumps(record), encoding="utf-8")
            env = {key: value for key, value in os.environ.items() if key != "PYTHONUTF8"}
            env["PYTHONIOENCODING"] = "cp1252"
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "validate-record", str(file)], capture_output=True, env=env, timeout=60)
            self.assertEqual(result.returncode, 1)
            parsed = json.loads(result.stdout.decode("utf-8"))
            self.assertTrue(any("file does not exist" in error for error in parsed["errors"]))
            self.assertFalse(any("codec" in error for error in parsed["errors"]))

    @unittest.skipUnless(tools.shutil.which("ffmpeg") and tools.shutil.which("ffprobe"), "FFmpeg and ffprobe are not on PATH")
    def test_real_media_round_trip(self):
        """Unmocked: generate a two-second silent clip and check it end to end."""
        with tempfile.TemporaryDirectory() as temp:
            media = Path(temp) / "silent.mp4"
            made = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=duration=2:size=160x120:rate=10", "-y", str(media)], capture_output=True, timeout=120)
            if made.returncode != 0:
                self.skipTest("this FFmpeg build cannot generate the fixture clip")
            self.assertEqual(tools.media_info(media, 60)["status"], "passed")
            result = tools.media_info(media, 60, require_audio=True)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["errors"], ["media: required audio stream is absent"])
            duration, error = tools.media_duration(media, 60)
            self.assertIsNone(error)
            self.assertAlmostEqual(duration, 2.0, delta=0.2)
            broken = Path(temp) / "broken.mp4"
            broken.write_bytes(media.read_bytes()[:200])
            self.assertNotEqual(tools.media_info(broken, 60)["status"], "passed")


class RevisionFiveRecordTests(unittest.TestCase):
    """Argument records, essay band notes, and bridges: the learner's words or nothing."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.parent = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def errors(self, value, **options):
        return tools.validate_record(value, self.parent, **options)

    def position(self):
        record = session()
        record["events"] = []
        record["position"] = {
            "question": "Does Hume's problem make science a kind of faith?",
            "first_claim": "Induction can't be justified, so science is faith.",
            "first_reason": "Every justification of induction uses induction.",
            "revised_claim": None,
            "what_moved": None,
            "open_question": None,
            "tutor_position": "Disagrees at the step from 'not justified deductively' to 'faith'.",
            "source_basis": "learner-account",
        }
        return record

    def test_position_record_accepts_pending_fields(self):
        self.assertEqual(self.errors(self.position()), [])

    def test_position_fields_are_null_or_the_learners_words(self):
        for key in ("first_claim", "revised_claim", "what_moved", "open_question"):
            for value in ("", 3, ["agent summary"]):
                with self.subTest(key=key, value=value):
                    record = self.position()
                    record["position"]["first_claim"] = record["position"]["first_claim"] or "x"
                    record["position"][key] = value
                    self.assertTrue(any(f"position.{key}" in error for error in self.errors(record)))

    def test_position_rejects_unknown_source_basis_and_orphan_revision(self):
        record = self.position()
        record["position"]["source_basis"] = "memory"
        self.assertTrue(any("source_basis" in error for error in self.errors(record)))
        record = self.position()
        record["position"]["first_claim"] = None
        record["position"]["revised_claim"] = "Science is a reasonable bet."
        self.assertTrue(any("revised_claim" in error for error in self.errors(record)))
        record = self.position()
        record["position"] = "they changed their mind"
        self.assertTrue(any("position" in error for error in self.errors(record)))

    def test_argument_template_is_a_valid_starter_and_not_a_record(self):
        record = tools.read_json(SCRIPT.parents[1] / "assets" / "argument-session.template.json")
        self.assertEqual(self.errors(record, allow_template=True), [])
        self.assertTrue(self.errors(record))

    def essay_bank(self):
        record = bank()
        record["items"][0].update(problem_id="phil-2023-q4", provenance="past-paper", source="papers/phil-2023.pdf, Q4", concepts=["utilitarianism"])
        record["items"][0]["attempts"][0].update(
            outcome="partial",
            band={"estimate": "Level 3 of 5", "descriptor_source": "papers/phil-descriptors.txt", "quoted": "arguments are stated but not weighed"},
            bridge="It's the same as checking a formula at a limit.",
        )
        return record

    def test_band_needs_the_criteria_it_was_judged_against(self):
        self.assertEqual(self.errors(self.essay_bank()), [])
        for mutate in (
            lambda band: band.pop("descriptor_source"),
            lambda band: band.update(descriptor_source="  "),
            lambda band: band.update(estimate=""),
            lambda band: band.update(quoted=""),
        ):
            record = self.essay_bank()
            mutate(record["items"][0]["attempts"][0]["band"])
            self.assertTrue(any("band" in error for error in self.errors(record)))
        record = self.essay_bank()
        record["items"][0]["attempts"][0]["band"] = "B+"
        self.assertTrue(any("band" in error for error in self.errors(record)))

    def test_bridge_is_text_or_absent(self):
        for value in ("", None, 4):
            with self.subTest(value=value):
                record = self.essay_bank()
                record["items"][0]["attempts"][0]["bridge"] = value
                self.assertTrue(any("bridge" in error for error in self.errors(record)))

    def test_existing_banks_without_the_new_fields_stay_valid(self):
        self.assertEqual(self.errors(bank()), [])


class RevisionFiveTimingTests(unittest.TestCase):
    # The test renderer writes only a marker. Content/decoding is a separate check.
    OUTPUT_FIXTURE = (
        "from pathlib import Path\nimport sys\n"
        "directory = Path(sys.argv[sys.argv.index('--media_dir') + 1])\n"
        "directory.mkdir(parents=True, exist_ok=True)\n"
        "suffix = '_ManimCE_v0.22.1.png' if '-s' in sys.argv else '.mp4'\n"
        "(directory / (sys.argv[-1] + suffix)).write_bytes(b'rendered')\n"
    )

    def invoke_timing(self, directory, command, *options):
        scene = directory / "lesson with spaces.py"
        scene.touch()
        process = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "render-timing", str(scene), "Example", "--manim", command, *options],
            cwd=directory, capture_output=True, encoding="utf-8", timeout=30,
        )
        return process.returncode, json.loads(process.stdout)

    def test_quoted_wrapper_reaches_the_renderer_with_intact_arguments(self):
        # The stand-in rejects a changed wrapper argument or split scene path.
        with tempfile.TemporaryDirectory(prefix="ppp argv ") as temp:
            root = Path(temp)
            wrapper = root / "fake renderer.py"
            wrapper.write_text(
                "import sys\n"
                "from pathlib import Path\n"
                "assert sys.argv[1] == 'one argument'\n"
                "if sys.argv[2:] == ['--version']:\n"
                "    print('test renderer')\n"
                "    sys.exit(0)\n"
                "assert sys.argv[2] == 'render'\n"
                "assert Path(sys.argv[-2]).name == 'lesson with spaces.py'\n"
                "assert sys.argv[-1] == 'Example'\n" + self.OUTPUT_FIXTURE,
                encoding="utf-8",
            )
            words = [sys.executable, str(wrapper), "one argument"]
            command = subprocess.list2cmdline(words) if os.name == "nt" else shlex.join(words)
            code, report = self.invoke_timing(root, command)
            self.assertEqual(code, 0, report)
            self.assertEqual(report["manim_version"], "test renderer")
            self.assertEqual([row["ok"] for row in report["runs"]], [True] * 3)

    def test_literal_executable_path_with_spaces_is_one_argument(self):
        import venv
        with tempfile.TemporaryDirectory(prefix="ppp path ") as temp:
            root = Path(temp)
            # This real interpreter accepts --version and executes the small
            # render stand-in. No renderer or external dependency is required.
            venv.EnvBuilder(with_pip=False).create(root / "test runtime")
            exe = root / "test runtime" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            (root / "render").write_text(self.OUTPUT_FIXTURE + "assert sys.argv[-1] == 'Example'\n", encoding="utf-8")
            code, report = self.invoke_timing(root, str(exe))
            self.assertEqual(code, 0, report)
            self.assertTrue(all(row["ok"] for row in report["runs"]))

    def test_kept_retry_preserves_prior_outputs_and_exposes_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            # Python doubles as a renderer here: --version succeeds, and its
            # next argument 'render' is a script in the current directory.
            (root / "render").write_text(
                "from pathlib import Path\nimport sys\n"
                "destination = Path(sys.argv[sys.argv.index('--media_dir') + 1])\n"
                "if Path('fail-preview').exists() and destination.name == 'preview':\n"
                "    sys.exit(7)\n"
                "destination.mkdir(parents=True, exist_ok=True)\n"
                "(destination / 'result.txt').write_text('completed', encoding='utf-8')\n" + self.OUTPUT_FIXTURE,
                encoding="utf-8",
            )
            code, first = self.invoke_timing(root, sys.executable, "--keep", str(root / "kept"))
            self.assertEqual(code, 0, first)
            (root / "fail-preview").touch()
            code, second = self.invoke_timing(root, sys.executable, "--keep", str(root / "kept"))
            self.assertEqual(code, 1, second)
            previous = first["runs"][1]["command"]
            current = second["runs"][1]["command"]
            old_dir = Path(previous[previous.index("--media_dir") + 1])
            new_dir = Path(current[current.index("--media_dir") + 1])
            self.assertTrue((old_dir / "result.txt").is_file())
            self.assertFalse((new_dir / "result.txt").exists(), "Failed retry reused a prior successful output")
            self.assertEqual(second["runs"][1]["returncode"], 7)
            self.assertIn("7", second["runs"][1]["error"])

    def test_missing_requested_scene_or_primary_artifact_is_a_failed_timing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "render").write_text(
                "from pathlib import Path\nimport sys\n"
                "root = Path(sys.argv[sys.argv.index('--media_dir') + 1])\n"
                "root.mkdir(parents=True)\n"
                "if '-s' in sys.argv:\n"
                "    (root / 'Other_ManimCE_v0.22.1.png').write_bytes(b'different scene')\n"
                "elif root.name == 'preview':\n"
                "    partial = root / 'partial_movie_files' / 'Example.mp4'\n"
                "    partial.parent.mkdir()\n"
                "    partial.write_bytes(b'incomplete')\n"
                "else:\n"
                "    (root / 'Example.mp4').touch()\n",
                encoding="utf-8",
            )
            code, report = self.invoke_timing(root, sys.executable)
            self.assertEqual(code, 1, report)
            self.assertEqual(report["status"], "failed")
            self.assertEqual([row["ok"] for row in report["runs"]], [False] * 3)
            for row in report["runs"]:
                self.assertEqual(row["returncode"], 0)
                self.assertIn("Example", row["error"])

    def test_project_output_directories_and_write_all_cannot_escape_the_attempt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            saved = root / "accepted" / "Example.mp4"
            saved.parent.mkdir()
            saved.write_bytes(b"accepted export")
            (root / "manim.cfg").write_text(
                "[CLI]\nwrite_all = True\nvideo_dir = " + saved.parent.as_posix()
                + "\nimages_dir = " + saved.parent.as_posix() + "\nbackground_color = RED\n",
                encoding="utf-8",
            )
            (root / "render").write_text(
                "import configparser,sys\nfrom pathlib import Path\n"
                "cfg = configparser.ConfigParser()\n"
                "cfg.read(sys.argv[sys.argv.index('--config_file') + 1] if '--config_file' in sys.argv else 'manim.cfg')\n"
                "opts = cfg['CLI']\n"
                "media = sys.argv[sys.argv.index('--media_dir') + 1]\n"
                "dest = Path(opts['images_dir' if '-s' in sys.argv else 'video_dir'].format(media_dir=media))\n"
                "dest.mkdir(parents=True, exist_ok=True)\n"
                "suffix = '.png' if '-s' in sys.argv else '.mp4'\n"
                "(dest / ('Example' + suffix)).write_bytes(b'timed scene')\n"
                "assert not opts.getboolean('write_all') and opts['background_color'] == 'RED'\n",
                encoding="utf-8",
            )
            code, report = self.invoke_timing(root, sys.executable, "--keep", str(root / "attempts"))
            self.assertEqual(saved.read_bytes(), b"accepted export")
            self.assertEqual(code, 0, report)

    def test_timeout_stops_a_launcher_child_before_it_can_write_late_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "render").write_text(
                "import subprocess, sys\nfrom pathlib import Path\n"
                "if Path(sys.argv[sys.argv.index('--media_dir') + 1]).name == 'preview':\n"
                "    subprocess.run([sys.executable, 'child.py'], check=True)\n"
                + self.OUTPUT_FIXTURE, encoding="utf-8",
            )
            (root / "child.py").write_text(
                "import time\nfrom pathlib import Path\nPath('ready').touch()\n"
                "deadline = time.monotonic() + 5\n"
                "while not Path('release').exists() and time.monotonic() < deadline:\n"
                "    time.sleep(0.01)\n"
                "Path('late-output').touch()\n", encoding="utf-8",
            )
            code, report = self.invoke_timing(root, sys.executable, "--timeout", "1")
            self.assertTrue((root / "ready").is_file(), "The descendant must start before the timeout")
            (root / "release").touch()
            time.sleep(0.4)
            self.assertFalse((root / "late-output").exists(), "The descendant survived its deadline")
            self.assertEqual(code, 1, report)
            self.assertEqual([row["ok"] for row in report["runs"]], [True, False, True])
            self.assertTrue(report["runs"][1]["timed_out"])

    def test_plan_times_three_renders_into_separate_directories_with_the_cache_off(self):
        plan = tools.timing_plan(["uv", "run", "manim"], Path("lesson.py"), "Lesson", 30, Path("media"))
        self.assertEqual([row["name"] for row in plan], ["still", "preview", "final"])
        directories = set()
        for row in plan:
            command = row["command"]
            self.assertEqual(command[:4], ["uv", "run", "manim", "render"])
            self.assertIn("--disable_caching", command)
            self.assertEqual(command[-2:], ["lesson.py", "Lesson"])
            directories.add(command[command.index("--media_dir") + 1])
        self.assertEqual(len(directories), 3)
        self.assertIn("-s", plan[0]["command"])
        self.assertEqual(plan[2]["command"][plan[2]["command"].index("--fps") + 1], "30")

    def test_timing_reports_failure_without_claiming_a_time_is_good(self):
        with tempfile.TemporaryDirectory() as temp:
            scene = Path(temp) / "lesson.py"
            scene.write_text("# fixture", encoding="utf-8")
            good = {"returncode": 0, "stdout": "Manim Community v0.22.1\n", "stderr": "", "timed_out": False}
            bad = {"returncode": 1, "stdout": "", "stderr": "NameError: Circel", "timed_out": False}
            media = Path(temp) / "media"
            for file in (media / "still/Lesson_ManimCE_v0.22.1.png", media / "final/Lesson.mp4"):
                file.parent.mkdir(parents=True)
                file.write_bytes(b"test artifact")
            with patch.object(tools, "render_command", side_effect=[good, good, bad, good]):
                result = tools.render_timing(["manim"], scene, "Lesson", 30, 10, media)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["manim_version"], "Manim Community v0.22.1")
            self.assertEqual([run["ok"] for run in result["runs"]], [True, False, True])
            self.assertIn("Circel", result["runs"][1]["error"])
            self.assertIn("this machine", result["limitation"])
            with patch.object(tools, "render_command", return_value=bad):
                self.assertEqual(tools.render_timing(["manim"], scene, "Lesson", 30, 10, Path(temp))["status"], "unavailable")
            self.assertEqual(tools.render_timing(["manim"], Path(temp) / "missing.py", "Lesson", 30, 10, Path(temp))["status"], "invalid")

    def test_cli_reports_a_missing_manim_command(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = tools.main(["render-timing", "lesson.py", "Lesson", "--manim", "definitely-not-a-real-manim-command"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "unavailable")

    def test_starter_scene_model_matches_its_hand_derived_values(self):
        """Runs the starter's own check; it must not need Manim installed."""
        scene = SCRIPT.parents[1] / "assets" / "manim" / "lesson_beats.py"
        result = subprocess.run([sys.executable, "-B", str(scene), "--check"], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("FAIL", result.stdout)
        self.assertGreaterEqual(result.stdout.count("pass"), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
