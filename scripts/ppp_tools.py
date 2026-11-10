#!/usr/bin/env python3
"""Small, dependency-free checks for PPP learning artifacts.

These checks validate structure and technical properties. They cannot establish
that a learner understood a concept or that a screenshot was actually inspected.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
from typing import Any
from urllib.parse import urlsplit


LIMITATION = (
    "Structural validation is not proof of learning, source authenticity, "
    "visual inspection, mathematical correctness, or perceptual media quality."
)
CAPTION_TOLERANCE_SECONDS = 0.05
STAMP = re.compile(r"^(\d{2,}):([0-5]\d):([0-5]\d),(\d{3})$")
# Narrow on purpose: a real topic such as "Template matching" must still pass.
TEMPLATE_TEXT = re.compile(r"\s*(Template(:| only\b)|Replace (with the|with verified|before logging)\b)")
BANK_LIMITATION = (
    "Review dates are planning choices recorded in this file. Nothing was scheduled, "
    "and a due item is a suggestion, not evidence about what the learner remembers."
)
PROVENANCE = ("past-paper", "generated", "source-adapted")
ASSISTANCE = ("none", "prompt", "hint", "partial", "full-solution")
OUTCOMES = ("not-attempted", "incorrect", "partial", "correct")


def finite_number(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def reject_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON number {value} is not permitted")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"Duplicate JSON key: {key}")
        obj[key] = value
    return obj


def read_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8-sig"),
        parse_constant=reject_constant,
        object_pairs_hook=unique_object,
    )


def aware_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})", value
    ):
        return None
    try:
        # strptime accepts 1-6 fraction digits consistently on Python 3.9+.
        pattern = "%Y-%m-%dT%H:%M:%S.%f%z" if "." in value else "%Y-%m-%dT%H:%M:%S%z"
        parsed = datetime.strptime(value.replace("Z", "+00:00"), pattern)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def iso_day(value: Any) -> date | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def template_markers(value: Any, path: str = "") -> list[str]:
    """Locate leftover template text so a starter file is not saved as a record."""
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            here = f"{path}.{key}" if path else str(key)
            if key == "template_notice":
                found.append(here)
            else:
                found.extend(template_markers(item, here))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(template_markers(item, f"{path}[{index}]"))
    elif isinstance(value, str) and TEMPLATE_TEXT.match(value):
        found.append(path)
    return found


def validate_record(record: Any, parent: Path, *, allow_template: bool = False) -> list[str]:
    """Return actionable schema errors. Never infer successful learning."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record: expected a JSON object"]
    if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        errors.append("schema_version: expected integer 1")
    kind = record.get("kind")
    if kind == "session":
        validate_session(record, errors)
    elif kind == "visual-evidence":
        validate_visual(record, parent, errors)
    elif kind == "question-bank":
        validate_bank(record, errors)
    else:
        errors.append("kind: expected session, visual-evidence, or question-bank")
    if not allow_template:
        for where in template_markers(record):
            errors.append(f"{where}: template placeholder text remains; replace or remove it, or pass --allow-template to check a starter file")
    return errors


def string_list(record: dict[str, Any], key: str, errors: list[str], *, required_items: bool = False) -> None:
    value = record.get(key)
    if not isinstance(value, list) or any(not nonempty(item) for item in value):
        errors.append(f"{key}: expected an array of nonempty strings")
    elif required_items and not value:
        errors.append(f"{key}: provide at least one item")


def validate_session(record: dict[str, Any], errors: list[str]) -> None:
    day = iso_day(record.get("date"))
    if day is None:
        errors.append("date: expected a valid YYYY-MM-DD date")
    elif (day - date.today()).days > 1:
        # One day of slack covers a session logged across a timezone boundary.
        errors.append("date: is in the future; record the day the session happened")
    if "inquiry" in record:
        inquiry = record["inquiry"]
        if not isinstance(inquiry, dict):
            errors.append("inquiry: expected an object")
        else:
            for key in ("question", "prediction", "observation", "open_question"):
                if key in inquiry and inquiry[key] is not None and not nonempty(inquiry[key]):
                    errors.append(f"inquiry.{key}: expected the learner's own words as a nonempty string, or null when none was given")
    for key in ("topic", "next_step"):
        if not nonempty(record.get(key)):
            errors.append(f"{key}: expected a nonempty string")
    string_list(record, "goals", errors, required_items=True)
    duration = record.get("duration")
    if not isinstance(duration, dict):
        errors.append("duration: expected an object")
    else:
        basis = duration.get("basis")
        seconds = duration.get("seconds")
        if "seconds" not in duration:
            errors.append("duration.seconds: required, use null when unknown")
        if basis not in ("unknown", "measured", "user-estimate"):
            errors.append("duration.basis: expected unknown, measured, or user-estimate")
        if basis == "unknown":
            if seconds is not None:
                errors.append("duration.seconds: must be null when basis is unknown")
        elif not finite_number(seconds) or seconds < 0:
            errors.append("duration.seconds: expected a finite nonnegative number")
        for key in ("start", "end"):
            if key in duration and duration[key] is not None and aware_datetime(duration[key]) is None:
                errors.append(f"duration.{key}: expected an ISO timestamp with a timezone")
        if basis == "measured":
            start, end = aware_datetime(duration.get("start")), aware_datetime(duration.get("end"))
            if start is None or end is None:
                errors.append("duration: measured duration requires timezone-aware start and end")
            else:
                observed = (end - start).total_seconds()
                if observed < 0:
                    errors.append("duration: end must not precede start")
                elif finite_number(seconds) and abs(seconds - observed) > 0.000001:
                    errors.append(f"duration.seconds: expected {observed:g} from start and end")
    events = record.get("events")
    if not isinstance(events, list):
        errors.append("events: expected an array, use [] when no attempt occurred")
        return
    for index, event in enumerate(events):
        label = f"events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{label}: expected an object")
            continue
        if not nonempty(event.get("problem_id")):
            errors.append(f"{label}.problem_id: expected a nonempty string")
        if event.get("provenance") not in ("past-paper", "generated", "source-adapted"):
            errors.append(f"{label}.provenance: expected past-paper, generated, or source-adapted")
        if "source" not in event or (event["source"] is not None and not nonempty(event["source"])):
            errors.append(f"{label}.source: expected a nonempty string or null")
        if event.get("provenance") in ("past-paper", "source-adapted") and not nonempty(event.get("source")):
            errors.append(f"{label}.source: source provenance requires a source locator")
        if event.get("assistance") not in ("none", "prompt", "hint", "partial", "full-solution"):
            errors.append(f"{label}.assistance: expected none, prompt, hint, partial, or full-solution")
        if event.get("outcome") not in ("not-attempted", "incorrect", "partial", "correct"):
            errors.append(f"{label}.outcome: expected not-attempted, incorrect, partial, or correct")
        if not isinstance(event.get("evidence"), str):
            errors.append(f"{label}.evidence: expected a string")
        elif event.get("outcome") != "not-attempted" and not event["evidence"].strip():
            errors.append(f"{label}.evidence: an attempted event needs the actual response or a description of what was observed; only a not-attempted event may leave it empty")
        if event.get("attribution") not in ("learner-statement", "observed-work", "agent-inference"):
            errors.append(f"{label}.attribution: expected learner-statement, observed-work, or agent-inference")
        if type(event.get("transfer")) is not bool:
            errors.append(f"{label}.transfer: expected a boolean")
        if "independent_success" in event and type(event["independent_success"]) is not bool:
            errors.append(f"{label}.independent_success: expected a boolean")
        if event.get("independent_success") is True and not (
            event.get("outcome") == "correct"
            and event.get("assistance") == "none"
            and event.get("attribution") == "observed-work"
            and nonempty(event.get("evidence"))
        ):
            errors.append(f"{label}.independent_success: requires correct unaided observed work and evidence")


def validate_bank(record: dict[str, Any], errors: list[str]) -> None:
    """Check a question bank: what was seen, how it went, and when to look again."""
    items = record.get("items")
    if not isinstance(items, list):
        errors.append("items: expected an array, use [] for an empty bank")
        return
    seen: set[str] = set()
    for index, item in enumerate(items):
        label = f"items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: expected an object")
            continue
        problem_id = item.get("problem_id")
        if not nonempty(problem_id):
            errors.append(f"{label}.problem_id: expected a nonempty string")
        elif problem_id in seen:
            errors.append(f"{label}.problem_id: duplicates an earlier item: {problem_id}")
        else:
            seen.add(problem_id)
        if item.get("provenance") not in PROVENANCE:
            errors.append(f"{label}.provenance: expected past-paper, generated, or source-adapted")
        if "source" not in item or (item["source"] is not None and not nonempty(item["source"])):
            errors.append(f"{label}.source: expected a nonempty string or null")
        if item.get("provenance") in ("past-paper", "source-adapted") and not nonempty(item.get("source")):
            errors.append(f"{label}.source: source provenance requires a source locator")
        concepts = item.get("concepts")
        if not isinstance(concepts, list) or any(not nonempty(entry) for entry in concepts):
            errors.append(f"{label}.concepts: expected an array of nonempty strings")
        exposure = item.get("exposure")
        if exposure not in ("unseen", "exposed", "attempted", "worked"):
            errors.append(f"{label}.exposure: expected unseen, exposed, attempted, or worked")
        protected = item.get("protected")
        if type(protected) is not bool:
            errors.append(f"{label}.protected: expected a boolean")
        attempts = item.get("attempts")
        last: date | None = None
        if not isinstance(attempts, list):
            errors.append(f"{label}.attempts: expected an array, use [] when none occurred")
            attempts = []
        for number, attempt in enumerate(attempts):
            where = f"{label}.attempts[{number}]"
            if not isinstance(attempt, dict):
                errors.append(f"{where}: expected an object")
                continue
            day = iso_day(attempt.get("date"))
            if day is None:
                errors.append(f"{where}.date: expected a valid YYYY-MM-DD date")
            else:
                if (day - date.today()).days > 1:
                    errors.append(f"{where}.date: is in the future")
                if last is not None and day < last:
                    errors.append(f"{where}.date: attempts must be in date order")
                last = day
            if attempt.get("outcome") not in OUTCOMES[1:]:
                errors.append(f"{where}.outcome: expected incorrect, partial, or correct")
            if attempt.get("assistance") not in ASSISTANCE:
                errors.append(f"{where}.assistance: expected none, prompt, hint, partial, or full-solution")
            if "recall" not in attempt or attempt["recall"] not in (None, "again", "hard", "good", "easy"):
                errors.append(f"{where}.recall: expected the learner's own rating again, hard, good, or easy, or null when not asked")
        if attempts and exposure in ("unseen", "exposed"):
            errors.append(f"{label}.exposure: an item with attempts is attempted or worked")
        review = item.get("next_review")
        if "next_review" not in item or (review is not None and iso_day(review) is None):
            errors.append(f"{label}.next_review: expected a YYYY-MM-DD date or null")
        elif review is not None and last is not None and iso_day(review) < last:
            errors.append(f"{label}.next_review: must not precede the latest attempt")
        if protected is True and (exposure != "unseen" or attempts or review is not None):
            errors.append(f"{label}.protected: a paper kept for a fresh timed attempt must stay unseen, unattempted, and unscheduled; clear the flag when the learner sits it")


def due_items(record: dict[str, Any], on: date) -> list[dict[str, Any]]:
    """Unprotected items whose recorded review date has arrived, oldest first."""
    due = [
        item for item in record["items"]
        if item["protected"] is False and item["next_review"] is not None and iso_day(item["next_review"]) <= on
    ]
    return sorted(due, key=lambda item: (item["next_review"], item["problem_id"]))


def validate_visual(record: dict[str, Any], parent: Path, errors: list[str]) -> None:
    source = record.get("source")
    if not isinstance(source, dict):
        errors.append("source: expected an object")
    else:
        for key in ("title", "creator", "url"):
            if not nonempty(source.get(key)):
                errors.append(f"source.{key}: expected a nonempty string")
        if isinstance(source.get("url"), str):
            try:
                url = urlsplit(source["url"])
                if url.scheme not in ("http", "https") or not url.netloc:
                    raise ValueError
            except ValueError:
                errors.append("source.url: expected an HTTP(S) source URL")
    if aware_datetime(record.get("captured_at")) is None:
        errors.append("captured_at: expected an ISO timestamp with a timezone")
    status = record.get("visual_status")
    if status not in ("complete", "incomplete"):
        errors.append("visual_status: expected complete or incomplete")
    for key in ("observations", "transcript_claims", "interpretations"):
        string_list(record, key, errors)
    frames = record.get("frames")
    if not isinstance(frames, list):
        errors.append("frames: expected an array")
        frames = []
    if not frames and status != "incomplete":
        errors.append("frames: absent visual evidence requires visual_status=incomplete")
    times: list[float] = []
    all_inspected = bool(frames)
    for index, frame in enumerate(frames):
        label = f"frames[{index}]"
        if not isinstance(frame, dict):
            errors.append(f"{label}: expected an object")
            all_inspected = False
            continue
        name = frame.get("file")
        if not nonempty(name):
            errors.append(f"{label}.file: expected a relative file path")
        else:
            path = Path(name)
            try:
                resolved = (parent / path).resolve()
                if path.is_absolute() or not resolved.is_relative_to(parent.resolve()):
                    errors.append(f"{label}.file: must stay inside the record's directory")
                elif not resolved.is_file():
                    errors.append(f"{label}.file: file does not exist: {name}")
            except (OSError, ValueError) as exc:
                errors.append(f"{label}.file: invalid path: {exc}")
        stamp = frame.get("timestamp_seconds")
        if not finite_number(stamp) or stamp < 0:
            errors.append(f"{label}.timestamp_seconds: expected a finite nonnegative number")
        else:
            times.append(float(stamp))
        if not nonempty(frame.get("visible_timestamp")):
            errors.append(f"{label}.visible_timestamp: expected visible time text or a stated limitation")
        if type(frame.get("inspected")) is not bool:
            errors.append(f"{label}.inspected: expected a boolean")
        if frame.get("inspected") is not True:
            all_inspected = False
    if status == "complete" and not all_inspected:
        errors.append("visual_status: complete requires every supplied frame to be marked inspected")
    motion = record.get("motion_claim")
    if motion is not None:
        if not isinstance(motion, dict):
            errors.append("motion_claim: expected an object or null")
        else:
            basis = motion.get("basis")
            if basis not in ("ordered-frames", "playback"):
                errors.append("motion_claim.basis: expected ordered-frames or playback")
            if not nonempty(motion.get("evidence")):
                errors.append("motion_claim.evidence: describe observed playback or frame sequence")
            if basis == "ordered-frames" and (
                len(times) != len(frames)
                or len(times) < 2
                or any(right <= left for left, right in zip(times, times[1:]))
                or not all_inspected
            ):
                errors.append("motion_claim: ordered-frames requires at least two inspected frames with strictly increasing times")


def audit() -> dict[str, Any]:
    packages: dict[str, Any] = {}
    for dist in ("manim", "manimgl", "manimlib"):
        try:
            packages[dist] = {"installed": True, "version": importlib.metadata.version(dist)}
        except importlib.metadata.PackageNotFoundError:
            packages[dist] = {"installed": False, "version": None}
    commands = ("ffmpeg", "ffprobe", "uv", "latex", "pdflatex", "xelatex", "tectonic", "yt-dlp")
    return {
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "platform": sys.platform,
        "packages": packages,
        "executables": {name: shutil.which(name) for name in commands},
        "functional_verification": "not-run",
        "limits": "Package metadata and PATH discovery only. No rendering, typesetting, browser, network, or image-generation capability was tested.",
    }


def parse_stamp(text: str) -> float | None:
    match = STAMP.fullmatch(text.strip())
    if not match:
        return None
    hours, minutes, seconds, milliseconds = map(int, match.groups())
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def check_captions(text: str, duration: float) -> tuple[list[str], int]:
    """Validate complete SRT blocks against a separately supplied media duration."""
    errors: list[str] = []
    if not finite_number(duration) or duration <= 0:
        return ["duration: expected a finite positive number of seconds"], 0
    clean = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not clean:
        return ["captions: file is empty"], 0
    if clean.startswith("WEBVTT"):
        return ["captions: this is a WebVTT file; this check reads SRT only, so convert it or check it another way"], 0
    blocks = re.split(r"\n(?:[ \t]*\n)+", clean)
    last_end = 0.0
    for index, block in enumerate(blocks, 1):
        lines = block.splitlines()
        label = f"cue {index}"
        if len(lines) < 3:
            errors.append(f"{label}: expected cue number, timing line, and text")
            continue
        if not lines[0].strip().isdigit() or int(lines[0].strip()) != index:
            errors.append(f"{label}: expected sequential cue number {index}")
        pieces = lines[1].split(" --> ")
        if len(pieces) != 2:
            errors.append(f"{label}: expected HH:MM:SS,mmm --> HH:MM:SS,mmm")
            continue
        # Text after the end time is an optional cue setting such as X1:40.
        start, end = parse_stamp(pieces[0]), parse_stamp((pieces[1].split() or [""])[0])
        if start is None or end is None:
            errors.append(f"{label}: malformed timestamp; minutes and seconds must be 00 through 59")
            continue
        if end <= start:
            errors.append(f"{label}: end must be after start")
        if start < last_end:
            errors.append(f"{label}: overlaps or precedes the previous cue")
        if end > duration + CAPTION_TOLERANCE_SECONDS:
            errors.append(f"{label}: ends at {end:g}s, beyond media duration {duration:g}s plus 0.05s tolerance")
        if not any(line.strip() for line in lines[2:]):
            errors.append(f"{label}: missing caption text")
        last_end = end
    return errors, len(blocks)


def bounded_process(args: list[str], timeout: float) -> dict[str, Any]:
    try:
        result = subprocess.run(args, capture_output=True, text=True, errors="replace", timeout=timeout, check=False)
        return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "timed_out": False}
    except subprocess.TimeoutExpired:
        return {"returncode": None, "stdout": "", "stderr": f"Command exceeded {timeout:g}s timeout", "timed_out": True}
    except OSError as exc:
        return {"returncode": None, "stdout": "", "stderr": str(exc), "timed_out": False}


def media_duration(path: Path, timeout: float) -> tuple[float | None, str | None]:
    """Probe a media file's container duration in seconds, or explain why not."""
    if not path.is_file():
        return None, "media: file does not exist"
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        return None, "--media requires ffprobe on PATH; pass --duration instead"
    probe = bounded_process([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path.resolve())], timeout)
    if probe["returncode"] != 0:
        detail = probe["stderr"].strip() or f"exit status {probe['returncode']}"
        return None, f"media: ffprobe failed: {detail}"
    try:
        value = float(json.loads(probe["stdout"])["format"]["duration"])
    except (ValueError, TypeError, KeyError):
        return None, f"media: ffprobe reported no duration: {probe['stderr'].strip() or 'no detail'}"
    if not finite_number(value) or value <= 0:
        return None, "media: ffprobe reported a nonpositive duration"
    return value, None


def media_info(path: Path, timeout: float, *, require_audio: bool = False, require_video: bool = False) -> dict[str, Any]:
    if not path.is_file():
        return {"status": "invalid", "errors": ["media: file does not exist"], "limitation": LIMITATION}
    ffprobe, ffmpeg = shutil.which("ffprobe"), shutil.which("ffmpeg")
    if ffprobe is None or ffmpeg is None:
        return {"status": "unavailable", "errors": ["media-info requires ffprobe and ffmpeg on PATH"], "limitation": LIMITATION}
    full_path = str(path.resolve())
    probe = bounded_process([ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", full_path], timeout)
    if probe["returncode"] != 0:
        return {"status": "invalid", "probe": probe, "limitation": LIMITATION}
    try:
        metadata = json.loads(probe["stdout"])
    except (ValueError, TypeError):
        return {"status": "invalid", "errors": ["ffprobe returned malformed JSON"], "probe": probe, "limitation": LIMITATION}
    if not isinstance(metadata, dict):
        return {"status": "invalid", "errors": ["ffprobe JSON must be an object"], "limitation": LIMITATION}
    streams = metadata.get("streams", [])
    if not isinstance(streams, list) or not any(isinstance(item, dict) and item.get("codec_type") in ("audio", "video") for item in streams):
        return {"status": "invalid", "errors": ["media has no audio or video streams"], "metadata": metadata, "limitation": LIMITATION}
    audio_present = any(isinstance(item, dict) and item.get("codec_type") == "audio" for item in streams)
    video_present = any(isinstance(item, dict) and item.get("codec_type") == "video" for item in streams)
    errors: list[str] = []
    if require_audio and not audio_present:
        errors.append("media: required audio stream is absent")
    if require_video and not video_present:
        errors.append("media: required video stream is absent")
    decode = bounded_process(
        [ffmpeg, "-v", "error", "-xerror", "-nostdin", "-i", full_path, "-map", "0:v?", "-map", "0:a?", "-f", "null", "-"],
        timeout,
    )
    return {
        "status": "passed" if decode["returncode"] == 0 and not errors else "failed",
        "metadata": metadata,
        "audio_present": audio_present,
        "video_present": video_present,
        "required_streams": {"audio": require_audio, "video": require_video},
        "errors": errors,
        "decode": decode,
        "perceptual_review": "not-run",
        "limitation": LIMITATION,
    }


def emit(value: Any, output: Path | None = None) -> None:
    serialized = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    audit_parser = commands.add_parser("audit", help="Discover installed packages and executable paths without running them")
    audit_parser.add_argument("--output", type=Path)
    record_parser = commands.add_parser("validate-record", help="Check one session or visual-evidence JSON record")
    record_parser.add_argument("path", type=Path)
    record_parser.add_argument("--allow-template", action="store_true", help="Accept leftover placeholder text, for checking a starter file")
    due_parser = commands.add_parser("due", help="List question-bank items whose recorded review date has arrived")
    due_parser.add_argument("path", type=Path)
    due_parser.add_argument("--on", help="Day to check as YYYY-MM-DD, default today")
    caption_parser = commands.add_parser("check-captions", help="Check SRT syntax, ordering, and media bounds")
    caption_parser.add_argument("path", type=Path)
    length = caption_parser.add_mutually_exclusive_group(required=True)
    length.add_argument("--duration", type=float, help="Media duration in seconds")
    length.add_argument("--media", type=Path, help="Media file to probe for its duration with ffprobe")
    media_parser = commands.add_parser("media-info", help="Probe metadata and decode all audio/video streams")
    media_parser.add_argument("path", type=Path)
    media_parser.add_argument("--timeout", type=float, default=300.0, help="Maximum seconds per subprocess, default 300")
    media_parser.add_argument("--require-audio", action="store_true", help="Fail when no audio stream exists, for finished narrated lessons")
    media_parser.add_argument("--require-video", action="store_true", help="Fail when no video stream exists")
    args = parser.parse_args(argv)
    # A legacy console code page must not turn a real finding into an encoding error.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (OSError, ValueError):
            pass
    try:
        if args.command == "audit":
            emit(audit(), args.output)
            return 0
        if args.command == "validate-record":
            record = read_json(args.path)
            errors = validate_record(record, args.path.resolve().parent, allow_template=args.allow_template)
            emit({"status": "invalid" if errors else "structurally-valid", "errors": errors, "limitation": LIMITATION})
            return 1 if errors else 0
        if args.command == "due":
            record = read_json(args.path)
            errors = validate_record(record, args.path.resolve().parent)
            if not errors and record.get("kind") != "question-bank":
                errors = ["kind: due reads a question-bank record"]
            on = date.today() if args.on is None else iso_day(args.on)
            if on is None:
                errors.append("--on: expected a valid YYYY-MM-DD date")
            if errors:
                emit({"status": "invalid", "errors": errors, "limitation": BANK_LIMITATION})
                return 1
            due = due_items(record, on)
            protected = sum(1 for item in record["items"] if item["protected"])
            emit({"status": "listed", "on": on.isoformat(), "due_count": len(due), "due": due, "protected_count": protected, "item_count": len(record["items"]), "limitation": BANK_LIMITATION})
            return 0
        if args.command == "check-captions":
            duration, source = args.duration, "supplied"
            if args.media is not None:
                duration, problem = media_duration(args.media, 60.0)
                source = "probed"
                if problem is not None:
                    emit({"status": "invalid", "errors": [problem], "limitation": LIMITATION})
                    return 1
            errors, count = check_captions(args.path.read_text(encoding="utf-8-sig"), duration)
            emit({"status": "invalid" if errors else "structurally-valid", "cue_count": count, "duration_seconds": duration, "duration_source": source, "errors": errors, "tolerance_seconds": CAPTION_TOLERANCE_SECONDS, "limitation": LIMITATION})
            return 1 if errors else 0
        if not finite_number(args.timeout) or args.timeout <= 0:
            raise ValueError("timeout must be a finite positive number")
        result = media_info(args.path, args.timeout, require_audio=args.require_audio, require_video=args.require_video)
        emit(result)
        return 0 if result["status"] == "passed" else 1
    except (OSError, ValueError, OverflowError) as exc:
        emit({"status": "invalid", "errors": [str(exc)], "limitation": LIMITATION})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
