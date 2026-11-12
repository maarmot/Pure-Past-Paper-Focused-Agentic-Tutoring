"""Grade one masked packet without loading labels, version identities or implementation sources."""
import argparse
import tempfile
from pathlib import Path
from run_context import run

HERE = Path(__file__).resolve().parent
INSTRUCTIONS = """Independently judge synthetic tutor replies. For each case and each anonymized response, evaluate every frozen criterion in its listed order. Treat the responses as independent candidates; do not reward extra length or try to infer version identity. Recalculate mathematical results. P requires all clauses to be satisfied, partial means some were met with no direct contradiction, F means a criterion was omitted or contradicted. Mark each using exactly P, partial, or F, followed by a short concrete reason tied to the actual text. Return one JSON object with the input case IDs as keys. Each case maps each anonymized label to an array of ordered [grade,reason] pairs. Cover every label and criterion. Output only JSON; never use tools; no other context is required.

MASKED PACKET
"""

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("job", choices=["development", "primary1", "primary2", "second"])
    p.add_argument("neutral", type=Path)
    args=p.parse_args()
    dest=HERE/"grades"
    dest.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        combined=Path(tmp)/"judge.txt"
        combined.write_bytes(INSTRUCTIONS.encode("utf-8")+(HERE/"packets"/(args.job+".json")).read_bytes())
        run(combined,(dest/(args.job+".json")).resolve(),args.neutral.resolve())
