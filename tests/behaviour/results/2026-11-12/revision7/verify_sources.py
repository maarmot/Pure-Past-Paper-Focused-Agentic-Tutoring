"""Verify both source snapshots after the original primary candidate was superseded."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from make_packet import REFS, packet

HERE = Path(__file__).resolve().parent
BASELINE = "20b6f9bf06c1b962aaf7f5f99beae577ae96c30d"

def verify_arm(repo, revision, arm, evidence, splits):
    for split in splits:
        recorded = json.loads((evidence/"inputs"/arm/(split+".json")).read_text(encoding="utf-8"))
        case_root = evidence if split=="transfer" else HERE
        _, actual = packet(repo, revision, split, case_root)
        if actual != recorded:
            raise ValueError(f"Instruction snapshot or tutor packet mismatch: {arm} {split}")

def verify(repo, final_revision):
    repo = repo.resolve()
    verify_arm(repo, BASELINE, "baseline", HERE, ["development","heldout"])
    with tempfile.TemporaryDirectory() as temp:
        scratch = Path(temp)
        for filename in REFS:
            path = scratch / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(subprocess.check_output(["git","-C",str(repo),"show",BASELINE+":"+filename]))
        patch = json.loads((HERE/"primary-candidate.patch.json").read_text(encoding="utf-8"))
        if patch["baseline"] != BASELINE:
            raise ValueError("Primary patch baseline mismatch")
        data = ("\n".join(patch["lines"])+"\n").encode("utf-8")
        subprocess.run(["git","apply","--whitespace=nowarn","-"], input=data, cwd=scratch, check=True)
        verify_arm(scratch, "WORKTREE", "candidate", HERE, ["development","heldout"])
    verify_arm(repo, BASELINE, "baseline", HERE/"followup", ["transfer"])
    verify_arm(repo, final_revision, "final", HERE/"followup", ["transfer","development","heldout"])
    print("Verified eight input packets and all six source hashes for every evaluated instruction version.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("repository", type=Path)
    p.add_argument("candidate", help="final release Git revision or WORKTREE")
    args = p.parse_args()
    verify(args.repository, args.candidate)
