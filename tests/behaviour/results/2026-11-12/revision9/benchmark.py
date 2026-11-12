"""Run or check the frozen revision 9 dialogue experiment. Python 3.9+, Git."""
import argparse
import concurrent.futures
import difflib
import importlib.util
import json
from pathlib import Path
import re
import secrets
import tempfile
from datetime import datetime, timezone


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PREVIOUS = HERE.parent / "revision8" / "evaluate.py"
spec = importlib.util.spec_from_file_location("ppp_revision8_eval", PREVIOUS)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
read, write, sha = old.read, old.write, old.sha
PATHS = ["SKILL.md", "references/deliberate-practice.md", "references/tutoring.md",
         "references/study-habits.md", "references/provenance.md"]
TUTOR = ("Follow the tutoring instructions below. Give the next learner-facing reply. "
         "Use no tools. The conversation contains the learner's actual messages and your "
         "earlier replies for this exchange. Respond to the final message.")
SCALE = {"P": 2, "M": 1, "F": 0}


def frozen():
    receipt = read(HERE / "freeze.json")
    if set(receipt["sha256"]) != {"protocol.json", "cases.json"}:
        raise ValueError("Freeze receipt must identify both the protocol and the cases")
    for name, expected in receipt["sha256"].items():
        if sha((HERE / name).read_bytes()) != expected:
            raise ValueError("Frozen input changed: " + name)
    return read(HERE / "protocol.json"), read(HERE / "cases.json")


def baseline():
    rev = frozen()[0]["baseline"]
    return {p: old.git(REPO, "show", rev + ":" + p).decode("utf-8-sig").replace("\r\n", "\n") for p in PATHS}


def capture(stage, tree):
    original = baseline()
    patches = {}
    for p in PATHS:
        src = original[p].splitlines(keepends=True)
        if tree.is_file():
            content = tree.read_text(encoding="utf-8-sig") if p == PATHS[1] else original[p]
        else:
            content = (tree / p).read_text(encoding="utf-8-sig")
        dest = content.splitlines(keepends=True)
        edits = []
        for op, i, j, a, b in difflib.SequenceMatcher(None, src, dest, autojunk=False).get_opcodes():
            if op != "equal":
                edits.append([i, j, "".join(dest[a:b])])
        if edits:
            patches[p] = edits
    path = HERE / "snapshots" / (stage + ".json")
    if path.exists():
        raise ValueError("Stage already frozen")
    if stage == "r8":
        raise ValueError("r8 comes from the original Git object")
    write(path, {"captured_utc": datetime.now(timezone.utc).isoformat(), "patches": patches})


def source(stage):
    files = baseline()
    if stage != "r8":
        patch = read(HERE / "snapshots" / (stage + ".json"))["patches"]
        for p, edits in patch.items():
            lines = files[p].splitlines(keepends=True)
            for i, j, value in reversed(edits):
                lines[i:j] = [value]
            files[p] = "".join(lines)
    normal = {p: re.sub(r"(?im)^revision\s+\d+\.?\s*$", "", files[p]).strip() for p in PATHS}
    return "\n\n".join("[" + p + "]\n" + val for p, val in normal.items()), {p: sha(val.encode()) for p, val in normal.items()}


def trials(split):
    proto, cases = frozen()
    rows = {case["id"]: case for case in cases[split]}
    seen = {}
    result = []
    for case in proto["trials"][split]:
        seen[case] = seen.get(case, 0) + 1
        result.append((case + "." + str(seen[case]), rows[case]))
    return result


def tutor_prompt(dossier, turns, message):
    chat = [entry for turn in turns for entry in ({"learner": turn["learner"]}, {"tutor": turn["tutor"]})]
    chat.append({"learner": message})
    return TUTOR + "\n\n" + dossier + "\n\nCONVERSATION\n" + json.dumps(chat, ensure_ascii=False)


def check_record(record, trial_id, row, dossier, manifest, complete):
    if record["trial"] != trial_id or record["source"] != manifest:
        raise ValueError("Wrong source or trial")
    turns, metrics = record["turns"], record["metrics"]
    if (len(turns) != len(metrics) or len(turns) > len(row["turns"])
            or (complete and len(turns) != len(row["turns"]))):
        raise ValueError("Wrong turn count: " + trial_id)
    for index, (turn, meta) in enumerate(zip(turns, metrics)):
        question = row["turns"][index]
        prompt = tutor_prompt(dossier, turns[:index], question)
        if (turn["learner"] != question or not turn["tutor"].strip()
                or sha(prompt.encode()) != meta["prompt_sha256"] or meta["tool_calls"]):
            raise ValueError("Turn content, history or tool use: " + trial_id)


def run_trial(stage, trial_id, row, dossier, manifest, dest, neutral):
    path = dest / "turns" / stage / (trial_id + ".json")
    record = read(path) if path.exists() else {"trial": trial_id, "source": manifest, "turns": [], "metrics": []}
    check_record(record, trial_id, row, dossier, manifest, False)
    for question in row["turns"][len(record["turns"]):]:
        prompt = tutor_prompt(dossier, record["turns"], question)
        reply, metric = old.model(prompt, neutral)
        if not reply.strip():
            raise ValueError("Empty reply")
        record["turns"].append({"learner": question, "tutor": reply})
        record["metrics"].append(metric)
        write(path, record)
    print("Complete", stage, trial_id, flush=True)


def run(split, stage, dest):
    dossier, manifest = source(stage)
    with tempfile.TemporaryDirectory() as temp, concurrent.futures.ThreadPoolExecutor(3) as pool:
        jobs = [pool.submit(run_trial, stage, key, row, dossier, manifest, dest, Path(temp))
                for key, row in trials(split)]
        for job in concurrent.futures.as_completed(jobs):
            job.result()


def make_packet(split, keys, dest):
    packet = []
    if set(keys["arms"]) != {key for key, _ in trials(split)}:
        raise ValueError("Missing or extra trial mapping")
    for key, row in trials(split):
        labels = keys["arms"][key]
        if set(labels) != {"X", "Y"} or set(labels.values()) != set(keys["comparison"]):
            raise ValueError("Invalid assignment")
        samples = {}
        for label, stage in labels.items():
            record = read(dest / "turns" / stage / (key + ".json"))
            check_record(record, key, row, *source(stage), complete=True)
            samples[label] = record["turns"]
        packet.append({"case": key, "criteria": row["criteria"], "samples": samples})
    return packet


def mask(split, pre, post, dest):
    keypath = dest / "masks" / (split + ".json")
    if keypath.exists() or pre == post:
        raise ValueError("Require separate stages and fresh mask")
    arms = {}
    for key, _ in trials(split):
        pair = [pre, post]
        secrets.SystemRandom().shuffle(pair)
        arms[key] = dict(zip(["X", "Y"], pair))
    keys = {"comparison": [pre, post], "arms": arms}
    packet = make_packet(split, keys, dest)
    write(keypath, keys)
    write(dest / "packets" / (split + ".json"), packet)


def grade_prompt(packet):
    return old.JUDGE + "\n" + json.dumps(packet, ensure_ascii=False)


def grade(split, which, dest):
    path = dest / "grades" / (split + "-" + which + ".json")
    if path.exists():
        raise ValueError("Preserve the existing judgment")
    packet = read(dest / "packets" / (split + ".json"))
    with tempfile.TemporaryDirectory() as temp:
        reply, metrics = old.model(grade_prompt(packet), Path(temp))
    raw = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", reply, flags=re.I)
    try:
        result = old.decode(raw)
        old.validate_grade(result, packet)
    except (ValueError, TypeError, KeyError, IndexError) as error:
        write(path.with_suffix(".invalid.json"), {"raw": reply, "metrics": metrics, "error": str(error)})
        raise
    write(path, {"grade": result, "metrics": metrics})


def results(split, dest):
    keys = read(dest / "masks" / (split + ".json"))
    pre, post = keys["comparison"]
    packet = make_packet(split, keys, dest)
    if packet != read(dest / "packets" / (split + ".json")):
        raise ValueError("Packet differs from reconstructed source")
    decoded = {}
    for judge in ["primary", "second"]:
        saved = read(dest / "grades" / (split + "-" + judge + ".json"))
        if (saved["metrics"]["prompt_sha256"] != sha(grade_prompt(packet).encode())
                or saved["metrics"]["tool_calls"]):
            raise ValueError("Grader received a different packet or used tools")
        old.validate_grade(saved["grade"], packet)
        by_trial = {}
        counts = {stage: dict.fromkeys(SCALE, 0) for stage in (pre, post)}
        for item in saved["grade"]["items"]:
            key = item["case"]
            stage = keys["arms"][key][item["label"]]
            ratings = [rating["rating"] for rating in item["ratings"]]
            by_trial.setdefault(key, {})[stage] = ratings
            for rating in ratings:
                counts[stage][rating] += 1
        direction, new_fails = {}, []
        for key, arms in sorted(by_trial.items()):
            old_sum, new_sum = (sum(SCALE[v] for v in arms[s]) for s in (pre, post))
            direction[key] = (new_sum > old_sum) - (new_sum < old_sum)
            for number, (a, b) in enumerate(zip(arms[pre], arms[post]), start=1):
                if a != "F" and b == "F":
                    new_fails.append([key, number])
        decoded[judge] = {"counts": counts, "direction": direction, "new_fails": new_fails, "ratings": by_trial}
    return {"comparison": [pre, post], "judges": decoded}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "evidence")
    cmd = parser.add_subparsers(dest="cmd", required=True)
    stage = cmd.add_parser("capture")
    stage.add_argument("stage")
    stage.add_argument("tree", type=Path)
    for operation in ("run", "mask", "grade", "results"):
        sub = cmd.add_parser(operation)
        sub.add_argument("split", choices=("cycle1", "cycle2", "cycle3", "final"))
        if operation == "run":
            sub.add_argument("stage")
        if operation == "mask":
            sub.add_argument("pre")
            sub.add_argument("post")
        if operation == "grade":
            sub.add_argument("judge", choices=("primary", "second"))
    args = parser.parse_args()
    if args.cmd == "capture":
        capture(args.stage, args.tree)
    elif args.cmd == "run":
        run(args.split, args.stage, args.out)
    elif args.cmd == "mask":
        mask(args.split, args.pre, args.post, args.out)
    elif args.cmd == "grade":
        grade(args.split, args.judge, args.out)
    else:
        print(json.dumps(results(args.split, args.out), indent=2))


if __name__ == "__main__":
    main()
