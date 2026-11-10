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
import subprocess
import sys
import tempfile
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
