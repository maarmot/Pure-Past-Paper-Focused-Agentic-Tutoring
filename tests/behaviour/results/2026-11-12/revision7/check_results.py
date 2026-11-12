"""Verify frozen inputs, packet identities, grade coverage and decoded totals. Standard-library Python."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
FREEZE = "bf81be5ce6daa64c911042fae5bc4e3a1ce028d6e03354bb302024ce7ee88304"
SPLITS = {"development": ["baseline-d1", "candidate-d1"],
          "heldout": ["baseline-h1", "baseline-h2", "candidate-h1", "candidate-h2"]}

def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key}")
        result[key] = value
    return result

def load(root, name):
    return json.loads((root / name).read_text(encoding="utf-8-sig"), object_pairs_hook=unique)

def require(result, message):
    if not result:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect(root=HERE):
    require(sha(root/"freeze.json") == FREEZE, "preregistration changed")
    for name, expected in load(root,"freeze.json").items():
        require(sha(root / name) == expected, f"changed frozen input: {name}")
    key = load(root,"key.json")
    cases = {}
    replies = {}
    for split,names in SPLITS.items():
        cs = load(root, split+".json")
        ids = {c["id"] for c in cs}
        require(len(cs)==len(ids), "duplicate fixture ID")
        for name in names:
            replies[name] = load(root, "replies/"+name+".json")
            require(set(replies[name])==ids, f"transcript coverage: {name}")
            require(all(isinstance(x,str) and x.strip() for x in replies[name].values()), f"blank reply: {name}")
        for c in cs:
            i=c["id"]
            cases[i]=c
            require(sorted(key[i].values())==sorted(names), f"mask identities: {i}")
            require(set(key[i])=={chr(65+j) for j in range(len(names))}, f"mask labels: {i}")
    require(set(cases)==set(key), "key coverage")
    job_ids={"development":["D1","D2","D3"], "primary1":[f"Q{x}" for x in range(1,7)],
             "primary2":[f"Q{x}" for x in range(7,13)], "second":["Q3","Q7","Q9"]}
    scores={}
    grouped={"heldout":{"baseline":Counter(),"candidate":Counter()},
             "development":{"baseline":Counter(),"candidate":Counter()}}
    differences=[]
    for job,ids in job_ids.items():
        packet=load(root, "packets/"+job+".json")
        grades=load(root, "grades/"+job+".json")
        require(set(packet)==set(grades)==set(ids), f"job coverage: {job}")
        for i in ids:
            row=packet[i]
            require(row["prompt"]==cases[i]["prompt"] and row["criteria"]==cases[i]["checks"], f"packet inputs: {i}")
            require(set(grades[i])==set(row["responses"])==set(key[i]), f"grade labels: {i}")
            for label, sample in key[i].items():
                require(row["responses"][label]==replies[sample][i], f"packet text: {i}/{label}")
                pairs=grades[i][label]
                require(isinstance(pairs,list) and len(pairs)==len(cases[i]["checks"]), f"criterion coverage: {i}/{label}")
                for index, pair in enumerate(pairs):
                    require(isinstance(pair,list) and len(pair)==2, f"grade format: {i}/{label}")
                    grade,reason=pair
                    require(grade in ("P","partial","F") and isinstance(reason,str) and reason.strip(), f"grade/reason: {i}/{label}")
                    slot=(i,label,index)
                    if job=="second":
                        if grade!=scores[slot]:
                            differences.append([i,label,index+1,scores[slot],grade])
                    else:
                        scores[slot]=grade
                        group="development" if job=="development" else "heldout"
                        grouped[group][sample.split("-")[0]][grade]+=1
    out={"decisions":{group:{arm:{s:counts[s] for s in ("P","partial","F")}
          for arm,counts in arms.items()} for group,arms in grouped.items()},
         "second_decisions":24, "disagreements":differences,
         "non_pass":[[i,label,key[i][label],index+1,grade] for (i,label,index),grade in scores.items() if grade!="P"]}
    return out

if __name__=="__main__":
    try:
        sys.path.insert(0, str(HERE/"followup"))
        from check_followup import inspect as inspect_followup
        result={"primary":inspect(),"followup":inspect_followup()}
        require(result == load(HERE,"summary.json"), "published summary differs from recomputed grades")
        print(json.dumps(result,indent=2))
    except (KeyError, ValueError, OSError) as exc:
        sys.exit(str(exc))
