"""Reproduce the exact frozen tutor packets from a Git revision or candidate working tree."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REFS = ["SKILL.md", "references/tutoring.md", "references/study-habits.md",
        "references/roadmaps.md", "references/end-to-end.md", "references/tools.md"]

def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def write(path, value):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

def digest(data):
    return hashlib.sha256(data).hexdigest()

def packet(repo, revision, split, case_root=ROOT):
    parts = ["Act as the invoked tutor described by this instruction packet. Each synthetic learner message is a new conversation. Reply exactly as you would to that learner. No learner answers may be invented. There is no live learner, file access or external tool in this text-only simulation. All fixture facts are in the messages. Do not use tools. Return a JSON object keyed by case ID with the complete learner-facing reply as its string value, without commentary.\n"]
    manifest = {}
    for name in REFS:
        data = (repo / name).read_bytes() if revision == "WORKTREE" else subprocess.check_output(
            ["git", "-C", str(repo), "show", revision + ":" + name])
        raw = data.decode("utf-8").replace("\r\n", "\n")
        manifest[name] = digest(raw.encode("utf-8"))
        parts += [f"\n<source file='{name}'>\n{raw}\n</source>\n"]
    cases = json.loads((case_root/(split + ".json")).read_text(encoding="utf-8"))
    parts += ["\nSynthetic messages, each independent:\n",
              json.dumps([{k: c[k] for k in ("id", "prompt")} for c in cases], ensure_ascii=False)]
    text = "".join(parts).encode("utf-8")
    return text, {"sources": manifest, "packet_sha256": digest(text)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("revision")
    parser.add_argument("split", choices=["development", "heldout"])
    parser.add_argument("arm", choices=["baseline", "candidate"])
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result, manifest = packet(args.repo, args.revision, args.split)
    args.output.write_bytes(result)
    write(f"inputs/{args.arm}/{args.split}.json", manifest)

if __name__ == "__main__":
    main()
