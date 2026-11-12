# Revision 9 tutor-response experiment

Three proposed changes to the tutoring instructions missed their preregistered improvement thresholds. The first and third tied their respective controls on every criterion. In the second, the same written instruction helped one sampled turn and hurt another sample of the same learner message. All three changes were excluded from the release.

| Experiment | Prior → proposed, full / partial / fail | Paired trials better / tied / worse | Decision |
|---|---|---|---|
| Ambiguous goal, cold diagnostic, changed objective | 6/0/0 → 6/0/0 | 0/3/0 | Reject additional instruction |
| Diagnose the reasoning behind a number | 4/2/0 → 5/0/1 | 1/1/1 | Reject. One new failure |
| Feasible problem, hidden method, checked key | 6/0/0 → 6/0/0 | 0/3/0 | Reject additional instruction |

Both judges gave the counts shown in each row. Each row contains two distinct scenarios. The first scenario was sampled twice per arm, so three paired trials do not constitute three independent scenarios. All three candidate snapshots use revision 8 as their comparator because the previous change was rejected. The [candidate deltas](snapshots) reconstruct the exact routed texts from the original Git object.

On the three final control scenarios the actual release and revision 8 each received four full passes, zero partials and zero failures from each judge. The scenarios exercised a quick calculation with an injected handout instruction, an offline recommendation based on stale assisted work, and an easy generated problem with an immediate answer key. Across the experiment the judges agreed on all 44 duplicated criterion-by-arm decisions. The numerical decision gates, judge directions and token counts are available in the [decoded results](summary.json). [Final control conversations](evidence/packets/final.json)

The 12 paired trials produced 24 synthetic conversations over nine distinct scenarios. All 38 planned tutor turns and eight judge calls completed. Tutor calls reported 1,171,074 input tokens, including 565,760 cached, and 7,477 output tokens. Graders reported 166,875 input tokens, including 123,904 cached, and 8,300 output tokens. The CLI reported 343.98 seconds summed over tutor workers and 204.22 over judges. Workers overlapped. About 8 minutes 49 seconds elapsed between the case freeze and the final grade files appearing on the evaluation host; that interval includes waiting for snapshots.

## What happened in the dialogues

In cycle 1 the learner could not choose among physics course labels. All four sampled responses gave an immediately usable graph task. Both versions also honored the separate learner's change from constructing their own example to receiving a written disproof. Neither judge considered a choice such as faster before/after or positive/negative/zero a leading course label when the learner also had to explain the graph. The tasks still differ in how much reasoning their question format reveals. [Masked graph and oral-exam conversations](evidence/packets/cycle1.json)

In cycle 2 the learner reached the right derivative at zero using an unsupported rule. Revision 8's two probes were mathematically discriminating, but both omitted an explicit acknowledgment that the number was right. The variant acknowledged the correct number in one sample and asked for a single new calculation. Its other sample requested a prediction plus an independent derivation and omitted the acknowledgment. Both arms then supplied the missing step when requested. Both accepted the circuit learner's request to end the oral exam and give the algebra. The two judges agreed independently on the new failure. [Paired calculus and circuits conversations](evidence/packets/cycle2.json) · [First ratings](evidence/grades/cycle2-primary.json) · [Second ratings](evidence/grades/cycle2-second.json)

In cycle 3 all four FPGA questions allowed the learner to decide what could be inferred before revealing the key. Exhausting the allowed increments against the stated transitions leaves 6 and 22. Their difference is 16, so every subsequent whole-clock reading agrees. The two calculus items both repaired the equality constraint. From the stationary points and required extrema, a cubic must have derivative $ax(x-2)$ with $a>0$, giving $f(0)-f(2)=4a/3$. The rubrics awarded intermediate work. [Masked generation conversations](evidence/packets/cycle3.json)

The baseline's quartic transfer is feasible. With minima at −1 and 1, its derivative can be written $k(x^2-1)(x-r)$ with $k>0$ and $-1<r<1$. The required rise of 2 gives $4kr/3=2$, hence $0<r<1$. The candidate's transfer has the unique cubic $2x^3-12x^2+18x$. Its value at 0 is 0, its derivative vanishes at 1, and its second derivative crosses zero at 2, where its value is 4. The learner saw neither transfer solution. [Independent arithmetic checks](verify.py)

## Protocol and reproduction

The evaluator froze the [prompts and scoring criteria](cases.json), [replications and acceptance thresholds](protocol.json) at 20:12:15 UTC on 12 November 2026, before the first candidate was captured. [Freeze receipt](freeze.json). The implementation owner received the hypothesis categories and acceptance procedure before editing. Shared storage provides no technical access barrier between collaborators. All published prompts are exposed for future work.

Tutor and grader calls used separate ephemeral Codex CLI contexts in neutral directories with a read-only sandbox and the same existing account. Every tutor turn received the explicit entry text plus the four selected references, prior dialogue of its own arm, and the current message only. No tools ran inside those workers. Two fresh masked judge calls per comparison received randomized X/Y assignments and identical rubric packets. Both ratings were recorded before decoding. This tests explicitly loaded instructions. The evaluator did not measure automatic route selection, access to a journal, real missing hardware or human learning with this experiment. The sample is small, both judges share a model provider, and matching decisions are correlated. The CLI exposed no seed, backend model build, or dollar cost. The fixed follow-up messages cannot react like a learner to differences in the first answer.

From this directory in a full clone, run the following offline checks with Python 3.9+ and Git. They reconstruct tutor prompt hashes and grade packet hashes, check the mask against the saved transcripts, verify reference math and compare the release checkout's five routed texts against the final test condition. A later checkout should supply the revision 9 source directory as the release path.

```sh
python -B verify.py --check-release ../../../../..
python -B -m unittest discover -s . -p test_integrity.py -v
```

In CI on a later revision, run `python -B verify.py --release-rev ARCHIVED` from this directory. It locates the unique ancestor that introduced the release snapshot and checks that commit's skill and reference files. An explicit commit hash also works.

Integrity tests inject changed history, a changed final reply, missing grade coverage, a swapped mask, an incomplete transcript and a different judge input into scratch copies. The unmodified evidence must pass. A modified record must fail at its source binding, reconstructed packet or expected coverage. These checks verify internal consistency with the published captures. They cannot authenticate model authorship against deliberate replacement of the entire dataset. The underlying CLI wrapper is the repository's [revision 8 evaluator](../revision8/evaluate.py).

To collect a *new* sample, use a currently authenticated compatible Codex CLI and an empty output directory. From this directory, run the commands below. Substitute the other split and snapshot names from the table or saved masks. Only `run` and `grade` invoke the service. The two judge commands can run independently following mask creation.

```sh
python -B benchmark.py --out /path/to/scratch run cycle2 r8
python -B benchmark.py --out /path/to/scratch run cycle2 c2
python -B benchmark.py --out /path/to/scratch mask cycle2 r8 c2
python -B benchmark.py --out /path/to/scratch grade cycle2 primary
python -B benchmark.py --out /path/to/scratch grade cycle2 second
python -B benchmark.py --out /path/to/scratch results cycle2
```

## A learner trial

Choose one target the learner wants to perform unaided, such as deciding whether recorded states determine an unknown increment. Have someone reserve two comparable unfamiliar problem pairs and an answer key before instruction. Ask for an unaided baseline attempt on each, note any earlier exposure, and vary tutor order across pairs under the same aids and time. After each session collect an unseen solo attempt and score the first unsupported step and the completed argument. About one week later use a changed representation or constraint without showing a worked example first. Have a reviewer score anonymous solutions with a rubric agreed before the trial. Retain actual time, hints, missed sessions and corrections. One learner and two topic pairs can guide the next session; a broader causal or retention claim requires more observations.
