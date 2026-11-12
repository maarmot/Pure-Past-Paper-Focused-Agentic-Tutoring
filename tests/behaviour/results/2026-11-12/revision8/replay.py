"""Create or verify the supplemental exposed development comparison."""
import argparse
import json
import secrets
from types import SimpleNamespace
from pathlib import Path

from check import check_transcript, require
from evaluate import HERE, JUDGE, grade, read, sha, source, validate_grade, write

PLAN_HASH = "665aa695246eede06fd6a6cf520f9d0fb4be9a9f7571b1b4f1198770e4496042"

def material(root, key, sources):
    plan_path = root / "replay-plan.json"
    require(sha(plan_path.read_bytes()) == PLAN_HASH, "Changed supplemental criteria")
    plan = read(plan_path)
    packet = []
    for row in read(root / "development.json"):
        cid = row["id"]
        arms = key[cid]
        require(set(arms) == {"X","Y"} and set(arms.values()) == {"before","after"}, "Invalid replay key")
        entry = {"case":cid,"criteria":plan["cases"][cid],"samples":{}}
        for label in ("X","Y"):
            folder = "evidence" if arms[label] == "before" else "replay"
            record = read(root / folder / "runs" / "candidate" / (cid + ".json"))
            check_transcript(row, record, sources[arms[label]] if sources else None)
            entry["samples"][label] = record["turns"]
        packet.append(entry)
    return packet

def mask(root):
    key_path = root / "replay" / "key.json"
    require(not key_path.exists(), "Preserve existing replay key and grades")
    key = {}
    for row in read(root / "development.json"):
        names = ["before", "after"]
        secrets.SystemRandom().shuffle(names)
        key[row["id"]] = dict(zip(("X", "Y"), names))
    packet = material(root, key, None)
    write(key_path, key)
    write(root / "replay" / "packets" / "development.json", packet)

def check(root, sources=None):
    key = read(root / "replay" / "key.json")
    packet = material(root, key, sources)
    require(read(root / "replay" / "packets" / "development.json") == packet, "Exposed replay packets differ")
    report = read(root / "replay" / "grades" / "development-primary.json")
    require(sha((JUDGE + "\n" + json.dumps(packet, ensure_ascii=False)).encode()) == report["metrics"]["prompt_sha256"],
            "Wrong replay grading input")
    validate_grade(report["grade"], packet)
    return [{"case":i["case"],"version":key[i["case"]][i["label"]], "rating":i["ratings"][0]["rating"],
             "reason":i["ratings"][0]["reason"]} for i in report["grade"]["items"]]

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["mask","grade","check"])
    p.add_argument("--root", type=Path, default=HERE)
    p.add_argument("--repo", type=Path)
    p.add_argument("--candidate", default="HEAD")
    args = p.parse_args()
    if args.action == "mask":
        mask(args.root)
    elif args.action == "grade":
        grade(SimpleNamespace(split="development", judge="primary", out=args.root / "replay"))
    else:
        src = None
        if args.repo:
            src = {"before":source(args.repo,args.candidate,read(args.root / "development-overlay.json")),
                   "after":source(args.repo,args.candidate,read(args.root / "first-freeze-overlay.json"))}
        print(json.dumps(check(args.root, src), indent=2))
