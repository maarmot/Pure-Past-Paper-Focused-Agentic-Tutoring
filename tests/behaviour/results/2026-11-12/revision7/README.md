# Revision 7 tutor-response comparison

## Release result

**On four fresh conversations targeting the two weaknesses found in the first round, the repaired skill scored 16 pass / 0 partial / 0 fail, compared with 13 / 1 / 2 for the published baseline.** Each version had two sampled replies per conversation and two criteria per reply. Two fresh blinded graders agreed on all 32 ratings. The four examples were chosen for those weaknesses, so the comparison supports only a narrow claim about tutor replies on this sample.

In one absolute-value hint the baseline used a number-line explanation and withheld the missing answer, but left the learner's premise about nonnegative outputs implicit. Both baseline replies about a misattributed shared slide proposed replacing its text when the learner had authorized only their private notebook. Both repaired replies confined the proposed edit to the notebook. These failures concerned advice in a simulation. Neither tutor actually accessed the presentation or wrote a record. See the [fresh cases](followup/transfer.json), [primary ratings](followup/grades/transfer.json) and [independent ratings](followup/grades/second.json).

| Evaluation | Published baseline | Initial candidate | Repaired release |
|---|---:|---:|---:|
| Initial blind held-out grade | 47 / 1 / 0 | 44 / 4 / 0 | — |
| Same 12 prompts after repair, jointly regraded as regression only | 46 / 1 / 1 | 44 / 2 / 2 | 48 / 0 / 0 |
| Four fresh, targeted transfer cases, both blind judges | 13 / 1 / 2 | — | 16 / 0 / 0 |
| Three development controls | 6 / 0 / 0 | 6 / 0 / 0 | 6 / 0 / 0 |

All triples are pass / partial / fail. The 12 earlier prompts became exposed when they informed the repair, so the 48/48 replay is a regression check. A fresh set of masked judges reassessed the exact earlier replies alongside the repaired ones. They judged four Q8 storage-scope responses more severely than the original primary judge. No other original grade shifted. The [decoded summary](summary.json) preserves every original judgment and the four differences. Across both rounds the scored evidence comprises 97 learner-facing replies in 13 fresh tutor contexts. Grader contexts were separate. No real learner participated.

The [follow-up preregistration](followup/protocol.json) was frozen before the two repairs, and the new examples remained undisclosed to the implementation owner until the final instructions were frozen. The [first-candidate patch](primary-candidate.patch.json) reconstructs the exact six preloaded instructions for the original comparison from the baseline commit. Eight packet manifests cover all distinct version/split combinations. The [follow-up report](followup/README.md) includes replay, runtime and reproduction details.


## Initial candidate comparison

**The frozen candidate had three fewer full passes on this sample.** No criterion received a failure. Neither the count nor the second model's agreement establishes a change in independent human learning.

| Split | Baseline pass / partial / fail | Candidate pass / partial / fail |
|---|---:|---:|
| Held out, 48 criteria per version | 47 / 1 / 0 | 44 / 4 / 0 |
| Development, 6 criteria per version | 6 / 0 / 0 | 6 / 0 / 0 |

In **Q3**, all four replies honored the request to hide the missing root. Both candidate replies asked whether a negative number can square to a positive value. Neither addressed the learner's correct premise that the principal square root of 9 is positive. Both baseline replies connected that notation to the different question of which inputs square to 9. The independent second grader agreed on both candidate partials.

In **Q8**, all four replies retained one hinted event, kept duration unknown and made no write. Both candidate replies and one baseline reply suggested correcting or retiring derived records or the stale export without explicitly limiting that advice to authorized private storage. One baseline reply kept the proposed correction with the authorized journal. These are partial judgments about advice; no private files existed and no disclosure was observed. Q8 was outside the preregistered second-grader subset. The other ten held-out cases received full passes in both samples of each version. On the preselected Q3, Q7 and Q9 subset the second reviewer agreed with all 24 criterion grades. Every original row and rationale is retained.

All three development controls passed both criteria in both versions. Both versions directly returned 70 mm, gave an unrevealed numerical test of a proposed identity and correctly classified the AI-supplied FFT answer as worked. The scored sample contained 54 learner-facing replies in six tutor contexts and four fresh grader contexts. The [derived summary](summary.json) is reproduced by the checker.

## What was sampled

Twelve preregistered synthetic conversations cover a short deadline, a direct solution, rejecting a plan, a concealed hint, guessing, diagnostic uncertainty, escalation, a transfer task with units, unverifiable exam attribution, contradictory private records, interrupted work, a malicious malformed retrieval, a hardware-project milestone, stopping and declining a reminder. Three separate development controls check direct conversion, answer leakage and assisted work. See [held-out cases and criteria](heldout.json), [development controls](development.json), [protocol](protocol.json) and [freeze](freeze.json). Every case and grading clause was fixed before the skill edits. The implementation owner received the development themes and frozen hash before seeing any held-out results.

Each held-out version ran in two fresh tutor contexts, giving 24 single-turn replies and 48 criterion decisions per version. Each context answered the twelve cases as separate conversations in one packet. The development controls ran in one additional fresh context per version. A separate context graded each half of the held-out set. A second reviewer graded the preselected Q3, Q7 and Q9 replies independently. The development controls had a separate grader. These are model judgments on correlated responses. No human learner or grader took part.

The tutor input contains the core skill and the tutoring, study-habits, roadmaps, end-to-end and tools references. The same reference paths and learner prompts were supplied in both arms. This controlled text-only test bypasses discovery and preloads more references than a normal turn. The read-only CLI received each packet on stdin in a neutral directory with no file or external tool calls observed. The fixture describes hypothetical conditions. Successful wording on Q8 or Q9 establishes no actual storage or retrieval behavior. Other release checks cover executable behavior.

The baseline is published revision 6 at `20b6f9bf06c1b962aaf7f5f99beae577ae96c30d`. The original baseline CLI smoke run tested the transport. The scored baseline used the same Python stdin wrapper as the candidate. An intermediate candidate was replaced after independent source review corrected a signed-displacement example. No held-out grades were inspected or shared before the correction. Both candidate samples and its development context were regenerated, the key reshuffled, and all graders restarted. This first round uses only the signed-displacement-corrected candidate, before the later hint and privacy repairs. The [source manifests](inputs/candidate/heldout.json) record the preloaded files and exact packet hashes.

The grader received case text, criteria and fresh per-case opaque labels. It received no implementation source, key or version identity. Labels used OS-generated randomness through Python's SystemRandom, and the mapping was decoded after grading. The complete [replies](replies), [masked packets](packets), [grades](grades) and [key](key.json) allow an independent reader to challenge individual decisions. A saved packet establishes its contents; timing and the absence of other access rest on the execution setup. The CLI model identifier, temperature, seed and dollar charges were unavailable in the completion events. Both arms used the same CLI default. Account- or service-level differences invisible to the CLI remain possible.

## Reproduce the checks

From this evidence directory in a full Git clone:

```sh
python -B check_results.py
python -B -m unittest discover -s . -p test_evidence.py -v
python -B verify_sources.py ../../../../.. HEAD
```

For the source check, use the commit that introduced revision 7 in place of HEAD when running on a later version. Before that commit is created, WORKTREE selects the current candidate files. The source check regenerates all eight tutor packet hashes from the original source files with LF-normalized line endings. The checker reconstructs counts and disagreement from every grade and validates each packet against the exact learner-facing reply. The fault tests reject a changed frozen input, missing transcript, duplicated mask assignment, omitted label, incomplete criterion, invalid grade, substituted reply and duplicate JSON key. Three additional faults exercise the follow-up key, grading coverage and replay identity.

To resample, work in a fresh copy of this directory in scratch storage. Put the frozen JSON inputs and the Python scripts there, leaving old keys, replies and grades behind. Create an empty neutral working directory and directories for replies and metrics. Use `python make_packet.py REPO REVISION heldout baseline PACKET` to reconstruct an input. Repeat for each split and version, then run `python run_context.py PACKET replies/baseline-h1.json NEUTRAL_DIR` for each appropriate slot (h1 and h2 for held out, d1 for development). Keep the emitted metrics. Run `python mask.py`, then `python grade.py JOB NEUTRAL_DIR` for development, primary1, primary2 and second, followed by the checker. These require a logged-in Codex CLI with the flags in the runner. New model replies, masks and grades will vary. Historical totals reproduce from retained artifacts without network access.

## Real learner validation

Select matched, unseen problems targeting the same obstacle and collect a short unaided pretest. Counterbalance topic and skill-version order, give each equal tutoring time, and record what help was provided. Have someone blind to condition score the reasoning on an unseen unaided problem immediately and again about a week later, with the delayed problem changing the setup. Keep direct-answer satisfaction separate from later independent transfer. This small personal trial can guide the next change; repeated trials across topics and learners are needed for a broader conclusion.

## Runtime observations

| Context | Baseline seconds | Candidate seconds | Baseline input / output tokens | Candidate input / output tokens |
|---|---:|---:|---:|---:|
| Development | 6.92 | 5.79 | 28,628 / 108 | 28,867 / 111 |
| Held-out sample 1 | 38.76 | 39.35 | 29,206 / 1,152 | 29,445 / 1,174 |
| Held-out sample 2 | 34.85 | 36.94 | 29,206 / 1,097 | 29,445 / 1,148 |

These wall times include launching the process. Token counts include host context, the entire lab packet and any cache use. The [run metrics](metrics) retain cached token and reasoning counts separately. Runs shared the host and overlapped in time. This small comparison cannot isolate model inference cost or the latency of normal skill routing. Each grader also records its own run metrics beside the [full grades](grades).
