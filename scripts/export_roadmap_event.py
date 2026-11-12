"""Project one explicitly selected event from an authorized PPP v1 session into a new file."""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from ppp_tools import iso_day, read_json, template_markers, validate_record


SKILL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,95}")
CORE = ("problem_id", "source", "provenance", "outcome", "assistance", "attribution", "evidence",
        "transfer", "independent_success")
EXTENSION = ("activity", "retrieval_from", "confidence", "uncertainty", "corrected_on", "session_ref", "previously_seen")


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def short_text(value, maximum, blank=False):
    return isinstance(value, str) and (blank or bool(value.strip())) and len(value.encode("utf-16-le")) // 2 <= maximum


def attempt_id(value):
    return (short_text(value, 240) and value == value.strip()
            and not re.search(r"[\x00-\x1f\x7f]", value))


def project(record, ordinal, skill_id, legacy_id, session_ref):
    require(isinstance(record, dict) and record.get("kind") == "session", "Choose a PPP v1 session.")
    require(1 <= ordinal <= len(record["events"]), "Select an existing event by its one-based position.")
    require(SKILL_ID.fullmatch(skill_id), "Choose a supported roadmap skill ID.")
    origin = record["events"][ordinal - 1]
    stable = origin.get("attempt_id")
    require(stable is None or legacy_id is None or legacy_id == stable,
            "The event already has a stable ID. Keep it when importing.")
    stable = stable or legacy_id
    require(attempt_id(stable), "Supply a stable --id for a legacy event or correct an unsupported ID in the authoritative file.")
    require(record["date"] <= date.today().isoformat(), "The session is future-dated here. Check the date before projecting it.")
    require(short_text(origin["problem_id"], 500) and short_text(origin["evidence"], 8000, blank=True)
            and (origin["source"] is None or short_text(origin["source"], 8000)),
            "The selected event exceeds the exchange text limits.")
    event = {key: origin[key] for key in CORE if key in origin}
    event.update(attempt_id=stable, date=record["date"], skill_id=skill_id,
                 response_basis=origin.get("response_basis", "unknown"), activity="unspecified")
    extension = origin.get("roadmap", {})
    require(isinstance(extension, dict) and set(extension) <= set(EXTENSION) | {"skill_id", "retrieval_eligible"},
            "The selected event has an unsupported roadmap extension. Keep the source file.")
    require(extension.get("skill_id", skill_id) == skill_id,
            "The stored roadmap skill differs from --skill. Resolve the mapping before export.")
    for key in EXTENSION:
        if key in extension:
            event[key] = extension[key]
    require(event["activity"] in ("solve", "explain", "unspecified"), "The stored activity type is invalid.")
    require(event.get("confidence", "unknown") in ("low", "medium", "high", "unknown"), "The confidence value is invalid.")
    if event.get("retrieval_from") is not None:
        require(attempt_id(event["retrieval_from"]) and event["retrieval_from"] != stable, "The retrieval link is invalid.")
    if event.get("corrected_on") is not None:
        require(iso_day(event["corrected_on"]) and record["date"] <= event["corrected_on"] <= date.today().isoformat(),
                "The correction date is invalid.")
    if "uncertainty" in event:
        require(short_text(event["uncertainty"], 8000, blank=True), "The uncertainty text is invalid.")
    if session_ref is not None:
        event["session_ref"] = session_ref
    if "session_ref" in event:
        require(short_text(event["session_ref"], 500), "Use a short, nonempty session reference.")
    require("previously_seen" not in event or type(event["previously_seen"]) is bool, "Prior exposure must be a boolean.")
    if any(earlier["problem_id"] == event["problem_id"] for earlier in record["events"][:ordinal-1]):
        event["previously_seen"] = True
    if "retrieval_eligible" in extension:
        # The browser writes a v1 veto for familiar problems even when a later, linked cold check succeeded.
        # Restore only eligibility for that distinct check. The exposure flag still excludes all fresh gates.
        require(extension["retrieval_eligible"] is True and extension.get("previously_seen") is True
                and event.get("retrieval_from") and event.get("independent_success") is False
                and event["outcome"] == "correct" and event["assistance"] == "none"
                and event["attribution"] == "observed-work" and event["response_basis"] == "reasoned"
                and event["activity"] in ("solve", "explain") and event["transfer"] is False,
                "The scoped retrieval claim conflicts with the recorded observation.")
        del event["independent_success"]
    require(not template_markers(event), "Replace PPP template placeholders before exporting an observation.")
    return {"kind": "roadmap-evidence", "schema_version": 1, "event": event}


def write_new(destination, data):
    """Publish complete bytes under a new name, without replacing any existing file."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".ppp-export-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        if os.name == "nt":
            os.rename(temporary, destination)  # On Windows rename refuses an existing destination.
        else:
            os.link(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", type=Path)
    parser.add_argument("--event", required=True, type=int, help="One-based position of one selected event")
    parser.add_argument("--skill", required=True, help="Exact destination skill ID")
    parser.add_argument("--id", help="Stable attempt ID, required for a legacy event without one")
    parser.add_argument("--session-ref", help="Optional opaque source label to include in the projection")
    parser.add_argument("--output", required=True, type=Path, help="New file in your authorized private location")
    args = parser.parse_args()
    try:
        # read_json rejects duplicate keys and non-finite numbers before fields can be lost.
        try:
            record = read_json(args.session)
        except (OSError, ValueError, RuntimeError):
            raise ValueError("Could not read the session JSON. Check it locally.") from None
        require(isinstance(record, dict) and record.get("kind") == "session", "Choose a PPP v1 session.")
        require(not validate_record(record, args.session.parent),
                "The session did not pass PPP validation. Run validate-record locally for details.")
        packet = project(record, args.event, args.skill, args.id, args.session_ref)
        data = (json.dumps(packet, indent=2, ensure_ascii=True) + "\n").encode("ascii")
        write_new(args.output, data)
    except FileExistsError:
        print("Choose a new output file. The existing file was kept.", file=sys.stderr)
        return 1
    except (TypeError, RecursionError, UnicodeError, OSError):
        print("Could not finish the local export. Check the input and output location.", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print("Exported one selected observation. Review it before importing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
