"""Validate a public tutoring-evaluation bundle and recompute its counts.

Python 3.9+, standard library only. Run in the containing public bundle, or use
``python check_results.py --root PATH``. No replies are scored automatically.
Exit 0 means structural checks passed; exit 1 prints a JSON validation error.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


VERSIONS = ("baseline", "candidate")
RATINGS = ("PASS", "PARTIAL", "FAIL")
FROZEN_NAMES = {
    "heldout.json", "development.json", "fixture.json", "protocol.json",
    "beam_reference.json",
}


class EvidenceError(ValueError):
    """A bundle is missing required evidence or contains inconsistent evidence."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON object key: " + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise EvidenceError("Non-finite JSON number: " + value)


def read(root, relative):
    try:
        return json.loads((root / relative).read_text(encoding="utf-8-sig"),
                          object_pairs_hook=unique_object,
                          parse_constant=invalid_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("Cannot read valid JSON: " + str(relative)) from exc


def is_hex(value, length):
    return (isinstance(value, str) and len(value) == length
            and all(char in "0123456789abcdef" for char in value))


def same_json(left, right):
    # Python equality collapses True/1 and 1/1.0. Retained evidence must preserve
    # JSON value types as well as string contents; object member order is immaterial.
    options = {"ensure_ascii": False, "sort_keys": True, "separators": (",", ":")}
    return json.dumps(left, **options) == json.dumps(right, **options)


def is_relative_name(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and path.parts != ()


def verify_freeze(root):
    freeze = read(root, "freeze.json")
    require(isinstance(freeze, dict) and set(freeze) == FROZEN_NAMES,
            "freeze.json must list exactly the five required frozen inputs")
    for name, expected in freeze.items():
        require(is_hex(expected, 64), "Invalid SHA-256 in freeze.json: " + name)
        try:
            actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        except OSError as exc:
            raise EvidenceError("Missing frozen input: " + name) from exc
        require(actual == expected, "SHA-256 mismatch for frozen input: " + name)
    return freeze


def verify_manifest(root, protocol):
    manifest = read(root, "instruction-manifest.json")
    require(isinstance(manifest, dict), "instruction-manifest must be an object")
    for version, commit_key in (("baseline", "commit"), ("candidate", "base_commit")):
        row = manifest.get(version)
        require(isinstance(row, dict), "instruction-manifest missing " + version)
        require(is_hex(row.get(commit_key), 40),
                "instruction-manifest invalid " + version + " commit")
        require(row[commit_key] == protocol.get("baseline_commit"),
                "instruction-manifest baseline commit does not match frozen protocol")
        files = row.get("files")
        require(isinstance(files, dict) and bool(files),
                "instruction-manifest needs instruction files for " + version)
        for name, digest in files.items():
            require(is_relative_name(name) and is_hex(digest, 64),
                    "instruction-manifest invalid relative file/SHA-256: " + str(name))
    require(isinstance(manifest.get("conditions"), dict),
            "instruction-manifest conditions must be an object")
    return manifest


def multiply(left, right):
    product = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            product[i + j] += a * b
    return product


def integrate(polynomial, lower, upper):
    return sum((coefficient * (upper ** (power + 1) - lower ** (power + 1))
                / (power + 1) for power, coefficient in enumerate(polynomial)),
               Fraction(0))


def verify_beam(root):
    """Use exact virtual-work integrals, independent of frozen decimal answers.

    P=E=b=1 normalizes cancelling scale factors. M/P and V/P are integrated
    against the matching unit-load fields. Parameters are transcribed from
    frozen B1, B2 and D2 questions; no tutor reply supplies an expectation.
    """
    cases = (
        ("B1_initial", "cantilever", Fraction(12, 25), Fraction(3, 25), Fraction(3, 10), Fraction(2, 100)),
        ("B1_corrected", "cantilever", Fraction(12, 25), Fraction(3, 125), Fraction(3, 10), Fraction(2, 100)),
        ("B2", "simply_supported", Fraction(6, 5), Fraction(3, 25), Fraction(33, 100), Fraction(4, 100)),
        ("D2", "cantilever", Fraction(3, 5), Fraction(1, 5), Fraction(3, 10), Fraction(5, 100)),
    )
    reference = read(root, "beam_reference.json")
    require(isinstance(reference, dict), "beam_reference must be an object")
    literal = reference.get("literal_reference")
    expected_keys = {name + suffix for name, *_ in cases for suffix in ("_r", "_error")}
    require(isinstance(literal, dict) and set(literal) == expected_keys,
            "beam_reference literal_reference has missing/extra values")
    report = {}
    for name, support, length, depth, nu, budget in cases:
        area, inertia = depth, depth ** 3 / 12
        shear_modulus, kappa = 1 / (2 * (1 + nu)), Fraction(5, 6)
        if support == "cantilever":
            moment, shear, bound, halves = [length, Fraction(-1)], [Fraction(1)], length, 1
        else:
            moment, shear, bound, halves = [Fraction(0), Fraction(1, 2)], [Fraction(1, 2)], length / 2, 2
        bending = halves * integrate(multiply(moment, moment), Fraction(0), bound) / inertia
        shear_deflection = halves * integrate(multiply(shear, shear), Fraction(0), bound) / (kappa * shear_modulus * area)
        ratio = shear_deflection / bending
        total_error = shear_deflection / (bending + shear_deflection)
        for suffix, expected in (("_r", ratio), ("_error", total_error)):
            value = literal[name + suffix]
            require(type(value) in (int, float), "beam_reference nonnumeric " + name + suffix)
            actual = Fraction(str(value))
            require(abs(actual - expected) <= Fraction(1, 10 ** 13),
                    "beam_reference disagrees with exact virtual work: " + name + suffix)
        report[name] = {
            "support": support, "r_exact": str(ratio), "r": float(ratio),
            "error_exact": str(total_error), "error": float(total_error),
            "normalized_bending_exact": str(bending),
            "normalized_shear_exact": str(shear_deflection),
            "budget": float(budget), "meets_shear_budget": total_error <= budget,
        }
    return report


def load_cases(root, phase):
    cases = read(root, phase + ".json")
    require(isinstance(cases, list) and cases, phase + " frozen cases must be a nonempty list")
    by_id = {}
    for case in cases:
        require(isinstance(case, dict), phase + " frozen case must be an object")
        case_id = case.get("id")
        require(isinstance(case_id, str) and bool(case_id) and is_relative_name(case_id)
                and "/" not in case_id, phase + " has invalid frozen case id")
        require(case_id not in by_id, phase + " has duplicate frozen case id")
        require(isinstance(case.get("area"), str) and is_relative_name(case["area"])
                and "/" not in case["area"], case_id + " has invalid area")
        require(isinstance(case.get("messages"), list) and case["messages"]
                and all(isinstance(message, str) and message.strip() for message in case["messages"]),
                case_id + " has invalid frozen messages")
        require(isinstance(case.get("criteria"), dict) and case["criteria"]
                and {"correctness", "help_level"} <= set(case["criteria"]),
                case_id + " frozen criterion set must include correctness/help_level")
        by_id[case_id] = case
    return cases, by_id


def verify_ratings(ratings, slots, criteria, context):
    require(isinstance(ratings, dict) and set(ratings) == slots,
            context + " missing/extra rating slots")
    for slot, grades in ratings.items():
        require(isinstance(grades, dict) and set(grades) == criteria,
                context + "/" + slot + " has missing/extra criterion grades")
        for criterion, grade in grades.items():
            label = context + "/" + slot + "/" + criterion
            require(isinstance(grade, dict) and set(grade) == {"rating", "reason"},
                    label + " rating must contain exactly rating/reason")
            require(grade["rating"] in RATINGS, label + " has invalid rating")
            require(isinstance(grade["reason"], str) and grade["reason"].strip(),
                    label + " needs a nonempty reason")


def verify_public_row(row, case, slots, sample_count, needs_second):
    case_id = case["id"]
    fields = {"case", "replies", "key", "ratings"}
    if needs_second:
        fields.add("second_ratings")
    require(isinstance(row, dict) and set(row) == fields,
            case_id + " public row has missing/extra fields, including second_ratings")
    require(same_json(row["case"], case), case_id + " public row differs from frozen case")
    replies, key = row["replies"], row["key"]
    require(isinstance(replies, dict) and set(replies) == slots,
            case_id + " missing/extra reply slots")
    require(isinstance(key, dict) and set(key) == slots,
            case_id + " missing/extra version/sample key slots")
    pairs = []
    for slot in sorted(slots):
        reply, identity = replies[slot], key[slot]
        require(isinstance(reply, dict) and set(reply) == {"turns", "actions"},
                case_id + "/" + slot + " reply must contain exactly turns/actions")
        require(isinstance(reply["turns"], list) and len(reply["turns"]) == len(case["messages"])
                and all(isinstance(turn, str) and turn.strip() for turn in reply["turns"]),
                case_id + "/" + slot + " invalid or missing turns")
        require(isinstance(reply["actions"], dict), case_id + "/" + slot + " actions must be an object")
        require(isinstance(identity, dict) and set(identity) == {"version", "sample"}
                and identity["version"] in VERSIONS and type(identity["sample"]) is int
                and 1 <= identity["sample"] <= sample_count,
                case_id + "/" + slot + " invalid version/sample mapping")
        pairs.append((identity["version"], identity["sample"]))
    expected = {(version, sample) for version in VERSIONS for sample in range(1, sample_count + 1)}
    require(set(pairs) == expected and len(set(pairs)) == len(pairs),
            case_id + " duplicate/missing version/sample pairs")
    criteria = set(case["criteria"])
    verify_ratings(row["ratings"], slots, criteria, case_id + "/ratings")
    if needs_second:
        verify_ratings(row["second_ratings"], slots, criteria, case_id + "/second_ratings")


def verify_packet(root, relative, expected_rows, fixture, grading):
    packet = read(root, relative)
    context = str(relative)
    require(isinstance(packet, dict) and set(packet) == {"fixture", "grading", "cases"},
            context + " packet fields must be exactly fixture/grading/cases")
    require(same_json(packet["fixture"], fixture), context + " packet differs from frozen fixture")
    require(same_json(packet["grading"], grading), context + " packet differs from frozen grading")
    rows = packet["cases"]
    require(isinstance(rows, list), context + " packet cases must be a list")
    found = {}
    for row in rows:
        require(isinstance(row, dict) and set(row) == {"case", "replies"},
                context + " packet rows must contain only case/replies")
        require(isinstance(row["case"], dict) and isinstance(row["case"].get("id"), str),
                context + " packet has invalid case")
        case_id = row["case"]["id"]
        require(case_id not in found, context + " packet has duplicate case")
        found[case_id] = row
    require(set(found) == set(expected_rows), context + " packet has missing/extra cases")
    for case_id, expected in expected_rows.items():
        require(same_json(found[case_id], expected),
                context + " packet has different frozen case or exact reply/actions: " + case_id)


def empty_counts():
    return {rating: 0 for rating in RATINGS}


def empty_versions():
    return {version: empty_counts() for version in VERSIONS}


def compare(counts, criteria):
    baseline, candidate = counts["baseline"], counts["candidate"]
    guard_failures = [criterion for criterion in ("correctness", "help_level")
                      if criteria.get(criterion, empty_versions())["candidate"]["FAIL"]
                      > criteria.get(criterion, empty_versions())["baseline"]["FAIL"]]
    no_worse = candidate["PASS"] >= baseline["PASS"] and candidate["FAIL"] <= baseline["FAIL"]
    no_better = candidate["PASS"] <= baseline["PASS"] and candidate["FAIL"] >= baseline["FAIL"]
    if baseline == candidate:
        classification = "mixed" if guard_failures else "unchanged"
    elif no_worse:
        classification = "mixed" if guard_failures else "stronger"
    elif no_better:
        classification = "weaker"
    else:
        classification = "mixed"
    return {"classification": classification, "guard_passed": not guard_failures,
            "guard_failures": guard_failures,
            "delta": {rating: candidate[rating] - baseline[rating] for rating in RATINGS}}


def summarize(rows, grade_field="ratings"):
    aggregate, by_area, by_criterion, by_area_criterion = empty_versions(), {}, {}, {}
    nonpass = []
    for row in rows:
        case = row["case"]
        area = case["area"]
        by_area.setdefault(area, empty_versions())
        by_area_criterion.setdefault(area, {})
        for slot, grades in row[grade_field].items():
            identity = row["key"][slot]
            version = identity["version"]
            for criterion, grade in grades.items():
                rating = grade["rating"]
                by_criterion.setdefault(criterion, empty_versions())
                by_area_criterion[area].setdefault(criterion, empty_versions())
                aggregate[version][rating] += 1
                by_area[area][version][rating] += 1
                by_criterion[criterion][version][rating] += 1
                by_area_criterion[area][criterion][version][rating] += 1
                if rating != "PASS":
                    nonpass.append({"case": case["id"], "area": area, "slot": slot,
                                    "version": version, "sample": identity["sample"],
                                    "criterion": criterion, **grade})
    return {"case_count": len(rows), "aggregate": aggregate, "by_area": by_area,
            "by_criterion": by_criterion, "by_area_criterion": by_area_criterion,
            "comparisons": {area: compare(counts, by_area_criterion[area])
                            for area, counts in by_area.items()},
            "aggregate_comparison": compare(aggregate, by_criterion), "nonpass": nonpass}


def optional_rubric_review(root, heldout_rows, fixture, grading):
    """Report a separate interpretation sensitivity; never replace primary data."""
    has_review = (root / "rubric-review.json").exists()
    has_packet = (root / "rubric-review" / "packet.json").exists()
    require(has_review or not has_packet,
            "rubric-review/packet.json exists without rubric-review.json")
    if not has_review:
        return None
    review = read(root, "rubric-review.json")
    require(isinstance(review, dict), "rubric-review.json must be an object")
    case_id = review.get("case_id")
    require(isinstance(case_id, str) and case_id.strip(),
            "rubric-review.json needs a nonempty case_id")
    by_id = {row["case"]["id"]: row for row in heldout_rows}
    require(case_id in by_id, "rubric-review.json case_id must name an existing heldout case")
    for field in ("interpretation", "ambiguity"):
        require(isinstance(review.get(field), str) and review[field].strip(),
                "rubric-review.json needs a nonempty " + field)
    grades = review.get("grades")
    require(isinstance(grades, dict) and set(grades) == {case_id},
            "rubric-review.json grades must contain exactly the selected case_id")
    original = by_id[case_id]
    verify_ratings(grades[case_id], set(original["replies"]),
                   set(original["case"]["criteria"]), "rubric-review/" + case_id)
    verify_packet(root, "rubric-review/packet.json",
                  {case_id: {"case": original["case"], "replies": original["replies"]}},
                  fixture, grading)
    clarified = {**original, "ratings": grades[case_id]}
    alternative = [clarified if row["case"]["id"] == case_id else row
                   for row in heldout_rows]
    return {
        "case_id": case_id, "interpretation": review["interpretation"],
        "ambiguity": review["ambiguity"],
        "original_case_summary": summarize([original]),
        "clarified_case_summary": summarize([clarified]),
        "heldout_sensitivity": summarize(alternative),
        "additional_explanation": {key: value for key, value in review.items()
                                   if key not in {"case_id", "interpretation", "ambiguity", "grades"}},
        "status": "Separate interpretation sensitivity; original phase totals remain primary.",
    }


def validate(root):
    freeze = verify_freeze(root)
    protocol, fixture = read(root, "protocol.json"), read(root, "fixture.json")
    require(isinstance(protocol, dict) and isinstance(protocol.get("grading"), str),
            "Frozen protocol needs grading text")
    protocol_inputs = protocol.get("frozen_inputs")
    require(isinstance(protocol_inputs, list)
            and all(isinstance(name, str) for name in protocol_inputs)
            and len(protocol_inputs) == len(set(protocol_inputs))
            and set(protocol_inputs) == FROZEN_NAMES - {"protocol.json"},
            "Frozen protocol input list differs from freeze manifest")
    manifest = verify_manifest(root, protocol)
    beam = verify_beam(root)
    secondary = protocol.get("second_grader_cases")
    require(isinstance(secondary, list) and all(isinstance(item, str) for item in secondary)
            and len(secondary) == len(set(secondary)), "Invalid second_grader_cases")
    phases, second_rows, heldout_rows = {}, [], []
    for phase, sample_count in (("heldout", 3), ("development", 5)):
        cases, by_id = load_cases(root, phase)
        selected = set(secondary) if phase == "heldout" else set()
        require(selected <= set(by_id), "second_grader_cases missing from frozen heldout cases")
        expected_files = {case_id + ".json" for case_id in by_id}
        actual_files = {path.name for path in (root / phase).glob("*.json")}
        require(actual_files == expected_files, phase + " has missing/extra public case files")
        slots = {chr(ord("A") + index) for index in range(2 * sample_count)}
        public = {}
        for case in cases:
            case_id = case["id"]
            row = read(root, phase + "/" + case_id + ".json")
            verify_public_row(row, case, slots, sample_count, case_id in selected)
            public[case_id] = row
        areas = {case["area"] for case in cases}
        expected_packets = {area + ".json" for area in areas}
        if phase == "heldout":
            expected_packets.add("second-review.json")
        actual_packets = {path.name for path in (root / "packets" / phase).glob("*.json")}
        require(actual_packets == expected_packets, phase + " has missing/extra packet files")
        for area in sorted(areas):
            expected_rows = {case_id: {"case": row["case"], "replies": row["replies"]}
                             for case_id, row in public.items() if row["case"]["area"] == area}
            verify_packet(root, "packets/" + phase + "/" + area + ".json",
                          expected_rows, fixture, protocol["grading"])
        if phase == "heldout":
            expected_rows = {case_id: {"case": public[case_id]["case"], "replies": public[case_id]["replies"]}
                             for case_id in selected}
            verify_packet(root, "packets/heldout/second-review.json", expected_rows,
                          fixture, protocol["grading"])
            second_rows = [public[case["id"]] for case in cases if case["id"] in selected]
            heldout_rows = list(public.values())
        phases[phase] = summarize(list(public.values()))
    second_report = summarize(second_rows, "second_ratings")
    disagreements = []
    for row in second_rows:
        for slot, grades in row["ratings"].items():
            for criterion, primary in grades.items():
                second = row["second_ratings"][slot][criterion]
                if primary["rating"] != second["rating"]:
                    disagreements.append({"case": row["case"]["id"], "area": row["case"]["area"],
                                          "slot": slot, **row["key"][slot], "criterion": criterion,
                                          "primary": primary, "secondary": second})
    second_report["disagreements"] = disagreements
    report = {"valid": True, "frozen_sha256": freeze, "instruction_manifest": manifest,
            "beam_check": beam, "phases": phases, "second_review": second_report,
            "improvement_rule": protocol.get("improvement_rule"),
            "limitations": [
                "Checks structure, exact retained text/actions and arithmetic, not pedagogical content or source-reading truth.",
                "Retained blinded packets do not establish chronology, grader isolation or decoding only after grading.",
                "The freeze manifest is not an authenticated signature; changing both inputs and hashes requires external provenance checks.",
                "Instruction hashes are structurally checked; instruction source bytes must be checked against the referenced commits separately.",
                "Counts describe these model-rated fixtures, not learner improvement or population reliability.",
                "Exact beam checks address only the stipulated elementary shear-omission models, not actual hardware accuracy.",
            ]}
    review_report = optional_rubric_review(root, heldout_rows, fixture, protocol["grading"])
    if review_report is not None:
        report["rubric_review"] = review_report
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="Containing public evidence bundle (default: this script's directory)")
    args = parser.parse_args()
    try:
        report = validate(args.root.resolve())
    except EvidenceError as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
