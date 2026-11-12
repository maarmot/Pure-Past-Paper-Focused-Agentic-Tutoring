"""Rebuild every comparison from sources, transcripts and masked judge evidence."""
import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import re

import benchmark as bench


SPLITS = ("cycle1", "cycle2", "cycle3", "final")


def check_math():
    # F(x) = integral_0^(x^2) 2t dt = x^4. Use exact symmetric differences to
    # recover the derivative; cancel the h^2 term using two step lengths.
    def slope(x, h):
        return ((x + h)**4 - (x - h)**4) / (2*h)

    def exact_slope(x):
        return (4*slope(x, Fraction(1, 2)) - slope(x, Fraction(1))) / 3

    grid = [Fraction(i, 4) for i in range(-12, 13)]
    assert all(exact_slope(x) == 4*x**3 for x in grid)
    assert [x for x in grid if exact_slope(x) == 2*x*x] == [0, Fraction(1, 2)]
    for r1 in (1, 3, 100):
        for r2 in (1, 4, 100):
            before, after = Fraction(6, r1 + r2), Fraction(6, 2*r1 + r2)
            assert Fraction(1, 2) < after / before < 1
    # Entire admissible domain checked against the consecutive state sequence.
    states = (3, 9, 15, 5)
    increments = [k for k in range(32) if all((a+k) % 16 == b for a, b in zip(states, states[1:]))]
    assert increments == [6, 22]
    assert {(states[-1]+k) % 16 for k in increments} == {11}
    assert all((3+6*n) % 16 == (3+22*n) % 16 for n in range(32))
    # p'(x)=a*x*(x-2), a>0 for the required order of extrema.
    # Simpson quadrature is exact for a quadratic derivative. Its integral
    # over [0,2] equals the endpoint change; the zero-change proposal fails.
    for a in (Fraction(1, 3), Fraction(1), Fraction(27)):
        derivative = lambda x: a*x*(x-2)
        assert derivative(-1)>0 and derivative(1)<0 and derivative(3)>0
        drop = -(derivative(0)+4*derivative(1)+derivative(2))/3
        assert drop == 4*a/3 and drop>0
    # The r8 transfer requires unequal minima of a quartic at -1 and 1.
    # g'(x)=k*(x^2-1)*(x-r), with k>0, -1<r<1. Integrating yields
    # g(1)-g(-1)=4*k*r/3; a drop in the opposite direction would change r.
    for r in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):
        k = 3/(2*r)
        primitive = lambda x: k*(x**4/Fraction(4)-r*x**3/3-x*x/Fraction(2)+r*x)
        assert primitive(1)-primitive(-1) == 2
    # C3 transfer constraints uniquely determine 2*x^3-12*x^2+18*x.
    a, b, c, d = 2, -12, 18, 0
    assert d==0 and 3*a+2*b+c==0 and 12*a+2*b==0 and 8*a+4*b+2*c+d==4
    assert 6*a!=0  # second derivative crosses zero at the inflection point.
    assert abs(2)*3 + abs(-1)*2 == 8


def token_summary(metrics):
    usage = Counter()
    for m in metrics:
        usage.update(m["usage"] or {})
    return {"calls": len(metrics), "tokens": dict(usage),
            "summed_worker_seconds": round(sum(m["seconds"] for m in metrics), 2),
            "cli_versions": sorted({m["cli"] for m in metrics})}


def audit(dest):
    check_math()
    report = {}
    tutors, graders = [], []
    for split in SPLITS:
        result = bench.results(split, dest)
        pre, post = result["comparison"]
        first, second = result["judges"].values()
        same, total = 0, 0
        for trial, arms in first["ratings"].items():
            for stage in arms:
                a, b = arms[stage], second["ratings"][trial][stage]
                same += sum(x == y for x, y in zip(a, b))
                total += len(a)
                tutors.extend(bench.read(dest / "turns" / stage / (trial + ".json"))["metrics"])
        directions = []
        cleared = []
        for name, judge in result["judges"].items():
            graders.append(bench.read(dest / "grades" / (split+"-"+name+".json"))["metrics"])
            pos = {k.split(".")[0] for k, v in judge["direction"].items() if v > 0}
            directions.append(pos)
            delta = judge["counts"][post]["P"] - judge["counts"][pre]["P"]
            threshold = delta >= 0 if split == "final" else (delta > 0 and sum(judge["direction"].values()) > 0)
            cleared.append(threshold and not judge["new_fails"])
        hurdle = all(cleared) and (split == "final" or bool(directions[0] & directions[1]))
        report[split] = {"arms": [pre, post], "counts": {k:v["counts"] for k, v in result["judges"].items()},
                         "paired_directions": {k:v["direction"] for k, v in result["judges"].items()},
                         "new_fails": {k:v["new_fails"] for k, v in result["judges"].items()},
                         "judge_agreement": [same,total], "numerical_gate": hurdle}
    return {"comparisons": report, "tutor": token_summary(tutors), "judge": token_summary(graders)}


def release_check(get_text, stage):
    manifest = bench.source(stage)[1]
    for p in bench.PATHS:
        data = get_text(p).replace("\r\n", "\n")
        normalized = re.sub(r"(?im)^revision\s+\d+\.?\s*$", "", data).strip()
        if bench.sha(normalized.encode()) != manifest[p]:
            raise ValueError("Release differs from evaluated source: " + p)


def archive_commit():
    sentinel = (bench.HERE / "snapshots/release.json").relative_to(bench.REPO).as_posix()
    commits = bench.old.git(bench.REPO, "log", "--diff-filter=A", "--format=%H", "HEAD", "--", sentinel).decode().splitlines()
    if len(commits) != 1:
        raise ValueError("Expected one commit adding the final snapshot; use a full clone or the explicit release commit")
    return commits[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=bench.HERE / "evidence")
    binding = parser.add_mutually_exclusive_group()
    binding.add_argument("--check-release", type=Path)
    binding.add_argument("--release-rev", help="Full Git commit, tag, or ARCHIVED to find the original release commit")
    args = parser.parse_args()
    report = audit(args.out)
    if args.out.resolve() == (bench.HERE / "evidence").resolve():
        if report != bench.read(bench.HERE / "summary.json"):
            raise ValueError("Published counts or usage disagree with the reconstructed evidence")
    stage = report["comparisons"]["final"]["arms"][1]
    if args.check_release:
        release_check(lambda p: (args.check_release / p).read_text(encoding="utf-8-sig"), stage)
    if args.release_rev:
        rev = archive_commit() if args.release_rev == "ARCHIVED" else args.release_rev
        release_check(lambda p: bench.old.git(bench.REPO, "show", rev + ":" + p).decode("utf-8-sig"), stage)
        report["release_commit"] = rev
    print(json.dumps(report, indent=2))
