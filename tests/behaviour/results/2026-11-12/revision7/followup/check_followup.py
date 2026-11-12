"""Recalculate follow-up ratings and identify changes when the original replies are regraded."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

from compare import FREEZE, HERE, PARENT, get_replies, jobs
sys.path.insert(0, str(PARENT))
from check_results import require, unique

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique)

def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def original_scores():
    scores={}
    key=read(PARENT/"key.json")
    for job in ("primary1","primary2","development"):
        grades=read(PARENT/"grades"/(job+".json"))
        for case,labels in grades.items():
            for label,pairs in labels.items():
                for index,(grade,_) in enumerate(pairs):
                    scores[case,key[case][label],index]=grade
    return scores

def inspect():
    require(file_hash(HERE/"freeze.json")==FREEZE,"changed follow-up preregistration")
    for name,digest in read(HERE/"freeze.json").items():
        require(file_hash(HERE/name)==digest, "changed frozen follow-up file: "+name)
    key=read(HERE/"key.json")
    all_cases={}
    sources={}
    counts={}
    for split in ("transfer","heldout","development"):
        root=HERE if split=="transfer" else PARENT
        cs=read(root/(split+".json"))
        src=get_replies(split)
        expected={c["id"] for c in cs}
        require(len(expected)==len(cs), "duplicate case")
        require(all(set(x)==expected and all(isinstance(v,str) and v.strip() for v in x.values())
                    for x in src.values()), "transcript coverage: "+split)
        for c in cs:
            i=c["id"]
            all_cases[i]=c
            sources[i]=src
            require(sorted(key[i].values())==sorted(src), "unbalanced map: "+i)
            require(set(key[i])=={chr(65+j) for j in range(len(src))},"mask labels: "+i)
        arms={s.split("-")[0] for s in src}
        counts[split]={v:Counter() for v in sorted(arms)}
    counts["transfer_second"]={"baseline":Counter(),"final":Counter()}
    require(set(key)==set(all_cases), "key coverage")
    original=original_scores()
    first={}
    disagreement=[]
    rescore=[]
    non_pass=[]
    for job,ids in jobs().items():
        packet=read(HERE/"packets"/(job+".json"))
        grades=read(HERE/"grades"/(job+".json"))
        require(set(grades)==set(packet)==set(ids), "job coverage: "+job)
        for i in ids:
            p=packet[i]
            c=all_cases[i]
            require(p["prompt"]==c["prompt"] and p["criteria"]==c["checks"], "case mismatch: "+i)
            require(set(grades[i])==set(p["responses"])==set(key[i]), "grade coverage: "+i)
            for label,name in key[i].items():
                require(p["responses"][label]==sources[i][name][i], "reply mismatch: "+i)
                pairs=grades[i][label]
                require(len(pairs)==len(c["checks"]), "criterion count: "+i)
                for n,pair in enumerate(pairs):
                    require(isinstance(pair,list) and len(pair)==2, "invalid grade format")
                    grade,reason=pair
                    require(grade in ("P","partial","F") and isinstance(reason,str) and reason.strip(),"invalid grade")
                    slot=(i,name,n)
                    split=("transfer_second" if job=="second" else "transfer" if i.startswith("T")
                           else "development" if i.startswith("D") else "heldout")
                    counts[split][name.split("-")[0]][grade]+=1
                    if grade!="P":
                        non_pass.append([job,i,label,name,n+1,grade])
                    if job=="second":
                        if first[slot]!=grade:
                            disagreement.append([i,name,n+1,first[slot],grade])
                    else:
                        first[slot]=grade
                        if slot in original and original[slot]!=grade:
                            rescore.append([i,name,n+1,original[slot],grade])
    return {"decisions":{sp:{arm:{g:counter[g] for g in ("P","partial","F")}
            for arm,counter in arms.items()} for sp,arms in counts.items()},
            "second_disagreements":disagreement,"regrade_changes":rescore,"non_pass":non_pass}

if __name__=="__main__":
    print(json.dumps(inspect(),indent=2))
