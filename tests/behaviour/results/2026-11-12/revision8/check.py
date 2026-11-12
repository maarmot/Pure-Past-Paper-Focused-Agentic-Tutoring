"""Recompute frozen input, transcript, prompt and blinded grading checks without a model."""
import argparse
import json
from pathlib import Path
from evaluate import BASELINE, HERE, JUDGE, TUTOR, read, sha, source, validate_grade


def require(value, message):
    if not value:
        raise ValueError(message)


def check_freeze(root):
    frozen = read(root / "freeze.json")
    require(set(frozen["sha256"]) == {"protocol.json", "development.json", "heldout.json", "reserve.json"},
            "Incomplete freeze")
    for filename, digest in frozen["sha256"].items():
        require(sha((root / filename).read_bytes()) == digest, "Changed frozen file " + filename)
    target = read(root / "targeted-freeze.json")
    require(set(target["sha256"]) == {"targeted.json", "targeted-plan.json"}, "Incomplete targeted freeze")
    for filename, digest in target["sha256"].items():
        require(sha((root / filename).read_bytes()) == digest, "Changed targeted file " + filename)


def check_transcript(row, sample, source_packet=None):
    require(row["id"] == sample["case"], "Wrong case")
    turns, metrics = sample["turns"], sample["metrics"]
    require([t["learner"] for t in turns] == row["turns"] and len(turns) == len(metrics), "Incomplete turns")
    require(all(isinstance(t["tutor"], str) and t["tutor"].strip() for t in turns), "Missing tutor response")
    history = []
    for turn, stat in zip(turns, metrics):
        history.append({"learner": turn["learner"]})
        require(stat["tool_calls"] == [] and stat["seconds"] > 0, "Unexpected tool activity or invalid timing")
        require(all(stat["usage"].get(k, 0) > 0 for k in ("input_tokens", "output_tokens")), "Missing token usage")
        if source_packet is not None:
            text, manifest = source_packet
            require(sample["source"] == manifest, "Wrong tutor sources")
            prompt = TUTOR + "\n\n" + text + "\n\nCONVERSATION\n" + json.dumps(history, ensure_ascii=False)
            require(sha(prompt.encode()) == stat["prompt_sha256"], "Wrong tutor prompt")
        history.append({"tutor": turn["tutor"]})


def grades(ev, split, judge, packet):
    if judge == "second" and split == "heldout":
        packet = [p for p in packet if p["case"] in {"H2", "H3"}]
    grade = read(ev / "grades" / (split + "-" + judge + ".json"))
    prompt = JUDGE + "\n" + json.dumps(packet, ensure_ascii=False)
    require(grade["metrics"]["prompt_sha256"] == sha(prompt.encode()), "Wrong grading packet")
    validate_grade(grade["grade"], packet)
    return {(i["case"], i["label"]):[v["rating"] for v in i["ratings"]] for i in grade["grade"]["items"]}


def profile(scores):
    return {grade: scores.count(grade) for grade in ("P", "M", "F")}


def score(scores):
    return 2 * scores.count("P") + scores.count("M")


def run(root, split, sources=None, broad_replay=False):
    rows = read(root / (split + ".json"))
    ev = root / ("regression" if broad_replay else "evidence")
    keys = read(ev / "keys" / (split + ".json"))
    ids = [r["id"] for r in rows]
    require(len(set(ids)) == len(ids) and set(keys) == set(ids), "Incorrect key coverage")
    packet = []
    turns_per_arm = 0
    for row in rows:
        cid = row["id"]
        require(set(keys[cid]) == {"X", "Y"} and set(keys[cid].values()) == {"baseline", "candidate"},
                "Invalid permutations")
        item = {"case": cid, "criteria": row["criteria"], "samples": {}}
        for label in ("X", "Y"):
            arm = keys[cid][label]
            store = root / "evidence" if broad_replay and arm == "baseline" else ev
            sample = read(store / "runs" / arm / (cid + ".json"))
            check_transcript(row, sample, sources.get(arm) if sources else None)
            item["samples"][label] = sample["turns"]
        packet.append(item)
        turns_per_arm += len(row["turns"])
    require(packet == read(ev / "packets" / (split + ".json")), "Tutor transcript differs from masked packet")
    primary = grades(ev, split, "primary", packet)
    secondary = grades(ev, split, "second", packet) if split != "development" else {}
    all_scores = {"baseline": [], "candidate": []}
    cases_summary = {}
    disagreements, new_fails = [], []
    partial_or_failed = []
    for row in rows:
        cid = row["id"]
        pair, second = {}, {}
        for label, arm in keys[cid].items():
            vals = primary[cid, label]
            pair[arm] = vals
            all_scores[arm].extend(vals)
            for index, rating in enumerate(vals, 1):
                if rating != "P":
                    partial_or_failed.append([cid, arm, index, rating])
            if (cid, label) in secondary:
                second[arm] = secondary[cid, label]
                for index, (a, b) in enumerate(zip(vals, second[arm]), 1):
                    if a != b:
                        disagreements.append([cid, arm, index, a, b])
        for index, (base, candidate) in enumerate(zip(pair["baseline"], pair["candidate"]), 1):
            if base != "F" and candidate == "F":
                new_fails.append([cid, index])
        cases_summary[cid] = {arm: profile(vals) for arm, vals in pair.items()}
        cases_summary[cid]["candidate_minus_baseline"] = score(pair["candidate"]) - score(pair["baseline"])
        if second:
            cases_summary[cid]["second_difference"] = score(second["candidate"]) - score(second["baseline"])
    sign = lambda n: (n > 0) - (n < 0)
    second_direction_agrees = all(sign(v["candidate_minus_baseline"]) == sign(v["second_difference"])
                                  for v in cases_summary.values() if "second_difference" in v)
    totals = {arm: profile(vals) for arm, vals in all_scores.items()}
    gate = totals["candidate"]["P"] > totals["baseline"]["P"] and not new_fails and second_direction_agrees
    if split == "targeted":
        gate = gate and totals["candidate"]["M"] == totals["candidate"]["F"] == 0
    return {"cases": cases_summary, "turns_per_arm": turns_per_arm, "primary": totals,
            "new_candidate_fails": new_fails, "primary_non_pass": partial_or_failed,
            "second_ratings":sum(len(v) for v in secondary.values()),
            "disagreements":disagreements, "sample_improvement_gate":gate}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=HERE)
    p.add_argument("--repo", type=Path, help="Verify tutor packet hashes against a full Git repository")
    p.add_argument("--candidate", default="HEAD")
    p.add_argument("--dev-candidate", help="Optional isolated source directory for the earlier development run")
    p.add_argument("--splits", nargs="+", default=["development", "heldout", "targeted", "reserve"])
    p.add_argument("--broad-replay", action="store_true", help="Also check the exposed final six-case replay")
    a = p.parse_args()
    check_freeze(a.root)
    results = {}
    for s in a.splits:
        sources = None
        if a.repo:
            release = source(a.repo, a.candidate)
            interim = source(a.repo, a.candidate, read(a.root / "first-freeze-overlay.json"))
            sources = {"baseline": interim if s == "targeted" else source(a.repo, BASELINE),
                       "candidate": interim if s == "heldout" else release}
            if s == "development":
                if a.dev_candidate:
                    sources["candidate"] = source(Path(a.dev_candidate), "WORKTREE")
                elif (a.root / "development-overlay.json").is_file():
                    sources["candidate"] = source(a.repo, a.candidate, read(a.root / "development-overlay.json"))
        results[s] = run(a.root, s, sources)
    if a.broad_replay:
        sources = {"baseline":source(a.repo, BASELINE), "candidate":source(a.repo, a.candidate)} if a.repo else None
        results["exposed_broad_replay"] = run(a.root, "heldout", sources, broad_replay=True)
        if set(a.splits) == {"development", "heldout", "targeted", "reserve"} and (a.root / "summary.json").exists():
            require(results == read(a.root / "summary.json"), "Stored summary differs from raw grades")
    print(json.dumps(results, indent=2))
