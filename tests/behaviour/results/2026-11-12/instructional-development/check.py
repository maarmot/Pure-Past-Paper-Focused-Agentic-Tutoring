"""Rebuild the development packets and counts. Use a full Git checkout."""
import hashlib
import json
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
DATA = json.loads((HERE / "evidence.json").read_text(encoding="utf-8"))
# This split tested the earliest development reference. It predates both repairs.
FIRST_DEVELOPMENT_REFERENCE = "7dbef2771fc0f524d218f6a734f7fb678f6963d20b0e6d19883dc528c90f3d55"


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source(ref, path):
    if ref == "WORKTREE":
        return (ROOT / path).read_text(encoding="utf-8")
    return subprocess.check_output(["git", "show", ref + ":" + path], cwd=ROOT).decode("utf-8")


def check_choice_replay(release):
    replay = json.loads((HERE / "choice-replay.json").read_text(encoding="utf-8"))
    before = (HERE / "first-repair-reference.txt").read_text(encoding="utf-8")
    after = before
    for change in replay["second_repair_edits"]:
        assert after.count(change["previous"]) == 1
        after = after.replace(change["previous"], change["candidate"])
    for label, reference in [("before", before), ("after", after)]:
        row = replay["replays"][label]
        assert digest(reference) == row["reference_sha256"]
        parts = [source(release, path) for path in replay["instructions"][:-1]]
        parts.append(reference)
        first = (replay["prefix"] + "\n\n" + "\n\n".join(parts)
                 + "\n\nLearner: " + replay["first_message"])
        assert digest(first) == row["question_packet_sha256"]
        followup = first + "\n\nTutor: " + row["question"] + "\n\nLearner: " + replay["second_message"]
        assert digest(followup) == row["key_packet_sha256"]
    prior, revised = replay["replays"]["before"], replay["replays"]["after"]
    assert "x(t)=t^3-6t^2+9t" in prior["question"]
    assert "is its speed increasing or decreasing?" in prior["question"]
    assert "local minimum" in prior["key"]
    # Independent exact speeds on either side reject that minimum claim.
    t = Fraction(2)
    speed = lambda h: abs(3 * h * h - 12 * h + 9)
    assert speed(t - Fraction(1, 10)) == speed(t + Fraction(1, 10)) < speed(t)
    assert "x(t)=t^2-4t+3" in revised["question"] and "t=1" in revised["question"]
    assert "v=+3" in revised["question"] and "a=-2" in revised["question"]
    assert "at the origin, moving left" in revised["key"] and "Slowing down" in revised["key"]
    # A centered difference is exact for a quadratic; this independently checks direction.
    def position(t):
        return t * t - 4 * t + 3
    def velocity(t):
        h = Fraction(1, 100)
        return (position(t + h) - position(t - h)) / (2 * h)
    assert position(1) == 0 and velocity(1) == -2
    assert velocity(Fraction(19, 10)) < velocity(2) == 0 < velocity(Fraction(21, 10))
    print("Rebuilt four exposed-replay inputs and checked the original speed-extremum counterexample.")


def check(release):
    first_reference = (HERE / "candidate-reference.txt").read_text(encoding="utf-8")
    assert digest(first_reference) == FIRST_DEVELOPMENT_REFERENCE
    cases = DATA["cases"]
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids)) == 4
    frozen = json.dumps(cases, indent=2) + "\n"
    assert digest(frozen.replace("\n", "\r\n")) == DATA["case_sha256_windows_crlf"]
    visible = [{"id": c["id"], "learner_turns": c["conversation"]} for c in cases]
    replies = {}
    for arm, ref in [("baseline", DATA["baseline_ref"]), ("candidate", release)]:
        texts = [
            first_reference if path == "references/deliberate-practice.md" else source(ref, path)
            for path in DATA["instruction_paths"][arm]
        ]
        packet = (DATA["tutor_instruction"] + "\n\n" + "\n\n".join(texts)
                  + "\n\nCASES\n" + json.dumps(visible, ensure_ascii=False))
        assert digest(packet) == DATA["tutor_packet_sha256_lf"][arm]
        rows = DATA["replies"][arm]
        assert [row["id"] for row in rows] == ids
        replies[arm] = {row["id"]: row["reply"] for row in rows}
    packed = []
    for case in cases:
        key = DATA["mask_key"][case["id"]]
        assert set(key) == {"A", "B"} and set(key.values()) == {"baseline", "candidate"}
        masked = {label: replies[arm][case["id"]] for label, arm in key.items()}
        packed.append({**case, "replies": masked})
    judge_packet = DATA["judge_instruction"] + "\n" + json.dumps(packed, ensure_ascii=False)
    assert digest(judge_packet) == DATA["judge_packet_sha256_lf"]
    totals = {arm: Counter() for arm in replies}
    seen = set()
    for row in DATA["ratings"]:
        case, label = row["id"], row["variant"]
        assert (case, label) not in seen and len(row["ratings"]) == 2
        assert all(r in {"PASS", "PARTIAL", "FAIL"} for r in row["ratings"])
        seen.add((case, label))
        totals[DATA["mask_key"][case][label]].update(row["ratings"])
    assert seen == {(case, label) for case in ids for label in ("A", "B")}
    assert totals == {"baseline": Counter(PASS=8), "candidate": Counter(PASS=8)}
    print("Four development cases; revision 7 and the first pre-repair candidate reconstructed.")
    print("Criterion judgments:", totals)


if __name__ == "__main__":
    release = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    check(release)
    check_choice_replay(release)
