"""Construct per-case blinded packets from frozen messages and complete response texts."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8-sig"))

def save(name, obj):
    path = ROOT/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

def masked(split, names):
    cases = load(split+".json")
    outputs = {name: load("replies/"+name+".json") for name in names}
    ids = {c["id"] for c in cases}
    if any(set(replies) != ids for replies in outputs.values()):
        raise ValueError("Unexpected or missing transcript IDs")
    packet = {}
    key = {}
    for c in cases:
        order = list(names)
        random.SystemRandom().shuffle(order)
        labels = {chr(65+n): alias for n, alias in enumerate(order)}
        key[c["id"]] = labels
        packet[c["id"]] = {"prompt": c["prompt"], "criteria": c["checks"],
            "responses": {letter: outputs[alias][c["id"]] for letter,alias in labels.items()}}
    return packet,key

def main():
    if (ROOT/"key.json").exists():
        raise SystemExit("Existing key: choose a fresh workspace for a new comparison.")
    h,kh = masked("heldout",["baseline-h1","baseline-h2","candidate-h1","candidate-h2"])
    d,kd = masked("development",["baseline-d1","candidate-d1"])
    save("key.json", dict(kh, **kd))
    jobs = {"primary1":list(h)[:6], "primary2":list(h)[6:], "second":["Q3","Q7","Q9"], "development":list(d)}
    full = dict(h, **d)
    for name,ids in jobs.items():
        save("packets/"+name+".json", {n: full[n] for n in ids})

if __name__ == "__main__":
    main()
