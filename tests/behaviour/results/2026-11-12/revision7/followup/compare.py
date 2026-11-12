"""Build and check the follow-up comparison using the same tutor and grader setup as the first round."""
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
from make_packet import packet
from check_results import unique
from grade import INSTRUCTIONS
from run_context import run

BASELINE = "20b6f9bf06c1b962aaf7f5f99beae577ae96c30d"
FREEZE = "17e329d106aa7f5982f3746b22346551d5c9b1c7dbaa38ae0a365b12aeedf6a9"

def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"), object_pairs_hook=unique)

def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(value, indent=2, ensure_ascii=False)+"\n").encode())

def cases(split):
    return load((HERE if split=="transfer" else PARENT)/(split+".json"))

def build(repo, revision, split, arm, destination):
    data, manifest = packet(repo, revision, split, HERE if split=="transfer" else PARENT)
    destination.write_bytes(data)
    save(HERE/"inputs"/arm/(split+".json"), manifest)

def get_replies(split):
    code={"development":"d","heldout":"h","transfer":"t"}[split]
    count=1 if split=="development" else 2
    result={}
    for arm in (["baseline","final"] if split=="transfer" else ["baseline","candidate","final"]):
        root=PARENT if arm!="final" and split!="transfer" else HERE
        for n in range(1,count+1):
            tag=f"{arm}-{code}{n}"
            result[tag]=load(root/"replies"/(tag+".json"))
    return result

def jobs():
    return {"transfer":["T1","T2","T3","T4"],"second":["T1","T2","T3","T4"],
            "replay1":["Q1","Q2","Q3","Q4"], "replay2":["Q5","Q6","Q7","Q8"],
            "replay3":["Q9","Q10","Q11","Q12"],"development":["D1","D2","D3"]}

def mask():
    if (HERE/"key.json").exists():
        raise ValueError("Existing mask key; use a fresh scratch directory")
    key={}
    packets={}
    for split in ["transfer","heldout","development"]:
        replies=get_replies(split)
        for case in cases(split):
            i=case["id"]
            names=list(replies)
            random.SystemRandom().shuffle(names)
            key[i]={chr(65+n):v for n,v in enumerate(names)}
            packets[i]={"prompt":case["prompt"],"criteria":case["checks"],
                        "responses":{k:replies[v][i] for k,v in key[i].items()}}
    save(HERE/"key.json",key)
    for job,ids in jobs().items():
        save(HERE/"packets"/(job+".json"),{i:packets[i] for i in ids})

def grade(job, neutral):
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/"judge.txt"
        p.write_bytes(INSTRUCTIONS.encode("utf-8")+(HERE/"packets"/(job+".json")).read_bytes())
        (HERE/"grades").mkdir(exist_ok=True)
        run(p,HERE/"grades"/(job+".json"),neutral)

def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    buildp=sub.add_parser("build")
    buildp.add_argument("repo",type=Path)
    buildp.add_argument("revision")
    buildp.add_argument("split",choices=["transfer","heldout","development"])
    buildp.add_argument("arm",choices=["baseline","final"])
    buildp.add_argument("destination",type=Path)
    sub.add_parser("mask")
    gp=sub.add_parser("grade")
    gp.add_argument("job",choices=jobs())
    gp.add_argument("neutral",type=Path)
    args=parser.parse_args()
    if args.command=="build":
        build(args.repo,args.revision,args.split,args.arm,args.destination)
    elif args.command=="mask":
        mask()
    else:
        grade(args.job,args.neutral)

if __name__=="__main__":
    main()
