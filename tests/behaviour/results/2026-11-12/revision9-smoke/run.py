"""Replay one-sided release stress cases with fresh contexts. Use a new output directory."""
import argparse
import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('paired', HERE.parent / 'revision8/evaluate.py')
paired = importlib.util.module_from_spec(spec)
spec.loader.exec_module(paired)
FILES = ['SKILL.md','references/tutoring.md','references/deliberate-practice.md','references/study-habits.md']


def packet(repo, ref):
    contents = {}
    for path in FILES:
        raw = (repo / path).read_bytes() if ref == 'WORKTREE' else subprocess.check_output(['git','-C',str(repo),'show',ref+':'+path])
        contents[path] = raw.decode('utf-8').replace('\r\n','\n')
    return '\n\n'.join('['+p+']\n'+s for p,s in contents.items()), {p:paired.sha(s.encode()) for p,s in contents.items()}


def next_prompt(source, messages):
    return paired.TUTOR + '\n\n' + source + '\n\nCONVERSATION\n' + json.dumps(messages, ensure_ascii=False)


def verify(cases, source, hashes, directory):
    expected_files = {case['id'] + '.json' for case in cases}
    if {p.name for p in directory.iterdir()} != expected_files:
        raise ValueError('Incomplete or extra release smoke transcripts')
    for case in cases:
        record = paired.read(directory / (case['id'] + '.json'))
        messages = record['messages']
        turns = case['turns']
        if record['source'] != hashes or len(messages) != 2 * len(turns) or len(record['metrics']) != len(turns):
            raise ValueError('Source or turn count differs for ' + case['id'])
        for index, (learner, metrics) in enumerate(zip(turns, record['metrics'])):
            stop = 2 * index + 1
            if messages[stop - 1] != {'learner':learner} or not messages[stop].get('tutor', '').strip():
                raise ValueError('Missing or changed turn in ' + case['id'])
            digest = paired.sha(next_prompt(source, messages[:stop]).encode())
            if digest != metrics['prompt_sha256'] or metrics['tool_calls'] != []:
                raise ValueError('Prompt or tool use differs for ' + case['id'])
    print(f'Verified inputs and coverage of {len(cases)} release conversations.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('repo',type=Path)
    ap.add_argument('ref')
    ap.add_argument('output',type=Path)
    ap.add_argument('--check', action='store_true', help='Verify existing inputs and turn coverage offline')
    args = ap.parse_args()
    cases = paired.read(HERE/'cases.json')
    source, hashes = packet(args.repo, args.ref)
    if args.check:
        verify(cases, source, hashes, args.output)
        return
    args.output.mkdir(parents=True,exist_ok=False)
    def run(case):
        messages, metrics = [], []
        with tempfile.TemporaryDirectory() as directory:
            for learner in case['turns']:
                messages.append({'learner':learner})
                prompt = next_prompt(source, messages)
                answer, usage = paired.model(prompt, Path(directory))
                messages.append({'tutor':answer})
                metrics.append(usage)
        paired.write(args.output / (case['id']+'.json'),{'source':hashes,'messages':messages,'metrics':metrics})
    with ThreadPoolExecutor(3) as pool:
        list(pool.map(run, cases))
if __name__ == '__main__':
    main()
