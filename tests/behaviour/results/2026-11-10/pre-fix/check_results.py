"""Recompute the reported pre-fix ratings directly from anonymized replies and labels."""
from collections import Counter
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def score(case):
    name = case['case']['id']
    criterion_ids = [line.split('.')[0] for line in case['case']['criteria']]
    need(len(set(criterion_ids)) == len(criterion_ids), f'{name}: duplicate rubric entry')
    labels = set('WXYZ')
    raw = case['replies']
    need(len(raw) == 4 and {r['label'] for r in raw} == labels, f'{name}: four distinct replies required')
    need(all(r['turn_1'].strip() and len(r['turn_1'].split()) == r['words'] for r in raw), f'{name}: invalid raw reply or word count')
    key = case['key']
    need(set(key) == labels, f'{name}: incomplete label key')
    cells = {(c['revision'], c['sample']) for c in key.values()}
    need(cells == {(4,1),(4,2),(5,1),(5,2)}, f'{name}: incomplete sampling cells')
    grades = case['grading']['grades']
    need(len(grades) == 4 and {g['label'] for g in grades} == labels, f'{name}: incomplete or duplicate grades')
    counts = {str(v): Counter() for v in (4, 5)}
    for grade in grades:
        criteria = grade['criteria']
        need(len(criteria) == len(criterion_ids) and {c['id'] for c in criteria} == set(criterion_ids), f'{name}: rubric mismatch')
        for c in criteria:
            need(c['verdict'] in ('PASS','PARTIAL','FAIL') and c['reason'].strip(), f'{name}: invalid criterion judgment')
            counts[str(key[grade['label']]['revision'])][c['verdict']] += 1
    need(counts == case['counts'], f'{name}: wrong recorded tally')
    return counts


def main():
    root = Path(__file__).resolve().parent
    coverage = json.loads((root/'coverage.json').read_bytes())
    totals = {str(v):Counter() for v in (4,5)}
    cases = sorted((root/'cases').glob('*.json'))
    need([p.stem for p in cases] == sorted(coverage['completed']), 'Case list differs from coverage')
    for path in cases:
        case = json.loads(path.read_bytes())
        need(case['case']['id'] == path.stem, f'{path.name}: wrong case ID')
        counts = score(case)
        need(counts == coverage['per_scenario'][path.stem], f'{path.name}: summary mismatch')
        for revision, counts_for_version in counts.items():
            totals[revision].update(counts_for_version)
    need(totals == coverage['totals'], 'Overall tally differs from individual judgments')
    print(json.dumps({'scenarios':len(cases),'criterion_ratings':totals},indent=2))


if __name__ == '__main__':
    main()
