"""Check completeness and recompute descriptive counts for the release evaluation."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERDICTS = ('PASS', 'PARTIAL', 'FAIL')


def need(value, message):
    if not value:
        raise ValueError(message)


def tally():
    expected_ids = [f'E{i:02d}' for i in range(1, 16)] + [f'T{i}' for i in range(1, 6)]
    cases = sorted((ROOT / 'cases').glob('*.json'))
    need([p.stem for p in cases] == expected_ids, 'Expected fifteen first-turn and five two-turn cases')
    total = {v: Counter() for v in ('4', '5')}
    by_case = {}
    turn_count = 0
    for path in cases:
        row = json.loads(path.read_bytes())
        identifier = row['case']['id']
        need(identifier == path.stem, 'Wrong case id')
        labels = set('ABCDEF')
        need(all(set(row[k]) == labels for k in ('ratings', 'key', 'replies')), identifier + ': label mismatch')
        cells = {(cell['revision'], cell['sample']) for cell in row['key'].values()}
        need(cells == {(v, n) for v in (4, 5) for n in (1, 2, 3)}, identifier + ': missing sampling cell')
        need(('turn2' in row['case']) == identifier.startswith('T'), identifier + ': scenario type mismatch')
        turns = {'turn1', 'turn2'} if identifier.startswith('T') else {'turn1'}
        counts = {v: Counter() for v in ('4', '5')}
        for label in labels:
            reply = row['replies'][label]
            need(set(reply) == turns and all(v.strip() for v in reply.values()), identifier + ': missing reply')
            turn_count += len(reply)
            grades = row['ratings'][label]
            need(len(grades) == len(row['case']['criteria']), identifier + ': rubric length')
            version = str(row['key'][label]['revision'])
            for verdict, reason in grades:
                need(verdict in VERDICTS and reason.strip(), identifier + ': ungrounded verdict')
                counts[version][verdict] += 1
                total[version][verdict] += 1
        by_case[identifier] = {v: {s: counts[v][s] for s in VERDICTS} for v in total}
    return {'cases': len(cases), 'conversations': 6 * len(cases), 'tutor_replies': turn_count,
            'criterion_totals': {v: {s: total[v][s] for s in VERDICTS} for v in total}, 'per_case': by_case}


if __name__ == '__main__':
    observed = tally()
    need(observed == json.loads((ROOT / 'summary.json').read_bytes()), 'Reported counts differ from case files')
    cal = json.loads((ROOT/'calibration.json').read_bytes())
    agree = total = 0
    for item in cal['cases']:
        base = json.loads((ROOT/'cases'/(item['id']+'.json')).read_bytes())['ratings']
        need(set(base) == set(item['ratings']), 'Missing calibration reply')
        for label, grades in item['ratings'].items():
            need(len(base[label]) == len(grades), 'Missing calibration criterion')
            for (first, _), (second, reason) in zip(base[label], grades):
                need(second in VERDICTS and reason.strip(), 'Invalid calibration grade')
                agree += first == second
                total += 1
    need([agree,total] == [cal['exact_agreements'],cal['ratings_compared']], 'Calibration tally mismatch')
    target = json.loads((ROOT/'targeted.json').read_bytes())
    need({c['case']['id'] for c in target['cases']} == {'E12','E15'}, 'Expected both follow-up cases')
    for row in target['cases']:
        need({(v['edition'], v['sample']) for v in row['key'].values()} == {(v,n) for v in ('before','after') for n in (1,2,3)}, 'Missing retest cell')
        counts = {v: Counter() for v in ('before','after')}
        for label in 'ABCDEF':
            need(row['replies'][label]['turn1'].strip(), 'Missing retest reply')
            grades = row['ratings'][label]
            need(len(grades) == len(row['case']['criteria']), 'Missing retest criterion')
            for verdict, reason in grades:
                need(verdict in VERDICTS and reason.strip(), 'Invalid retest grade')
                counts[row['key'][label]['edition']][verdict] += 1
        need(counts == target['counts'][row['case']['id']], 'Retest tally mismatch')
    print(json.dumps({k: v for k, v in observed.items() if k != 'per_case'}, indent=2))
