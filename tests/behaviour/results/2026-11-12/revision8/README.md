# Revision 8 tutor-response evaluation

The six initial held-out conversations tied at 18 full passes per version. Two fresh cases aimed at the subsequent repair also tied, as did two general reserve cases. The experiment found defects worth addressing in development, but the held-out results do not establish a tutoring improvement.

| Comparison | Left version | Right version | Primary grades, left then right (pass / partial / fail) | Independent agreement |
|---|---|---|---|---|
| Two development cases | Published revision 7 | Initial draft | 5/1/0 → 6/0/0 | One judge |
| Six initial held-out cases | Published revision 7 | First repair | 18/0/0 → 18/0/0 | 14/14 repeated ratings on H2 and H3 |
| Two exposed development prompts, tighter supplemental anchors | Initial draft | First repair | 0/0/2 → 0/0/2 | One separate judge |
| Two fresh targeted cases | First repair | Final skill | 4/0/0 → 4/0/0 | 8/8 repeated ratings |
| Two general reserve cases | Published revision 7 | Final skill | 6/0/0 → 6/0/0 | 12/12 repeated ratings |
| Six exposed initial cases replayed | Original revision 7 replies | Final skill | 18/0/0 → 18/0/0 | 14/14 repeated ratings on H2 and H3 |

The [frozen primary plan](protocol.json) required a measured gain. No held-out comparison passed its improvement gate. Every planned pair was complete. No grader disagreements occurred on the 48 twice-scored decisions, including the 14 exposed replay decisions. Repeated ratings of the same text are correlated. The [decoded counts](summary.json), [masked grade reasons](evidence/grades), [development replay](replay/grades) and [final broad replay](regression/grades) retain the original judgments.

## Where the grades missed a defect

The initial development judge marked every draft criterion as a pass. Reading the two conversations uncovered a wrong-orientation sketch shown before its correction and a generated question that forced the learner to choose increasing or decreasing speed at an instant where its rate of change was zero. The two saved keys correctly found a local maximum. Neither the accurate key nor the corrected sketch repaired the first thing the learner saw. The baseline's partial on the original rubric concerned missing units on two derivative expressions.

We froze [two supplemental anchors](replay-plan.json) after discovering those defects and before sampling repaired replies. The first repair encouraged checking figures and wording against the key. Its new fencing diagram was consistent, but its deliberately simplified numerical example met only the fencing constraint. The reply explicitly told the learner it missed the area requirement. The strict rubric penalized this. A teacher might reasonably accept isolating one constraint while helping an overloaded learner. Its new quiz repeated the same wrong pair of alternatives. The stricter judge marked both arms fail on both anchors.

The second repair asks the tutor to work each subquestion with the displayed values and choose an actual offered answer before releasing it. The [targeted cases and criteria](targeted.json) and [comparison plan](targeted-plan.json) were frozen before those words changed. Both candidates included the zero rate in a temperature question and gave feasible integer loading examples. These two cases exposed no difference. Additional broad guidance was left alone. A separate implementation-owner replay is outside the masked counts.

## What the experiment exercised

H1 followed a vague goal into a concrete waveform challenge. H2 followed correct independent reasoning into a harder oral question, then requested the whole explanation and a stop. H3 generated a mechanics problem, hid the key, then checked the solution, marks and reveal boundary. H4 protected a quick answer and a curiosity detour. H5 tested an embedded instruction and uncertainty about two possible analog sources. H6 distinguished reported independent work, copied work and recognition after a narrowed correction. The reserve checked a counterexample with an explicit stop and a generated circuit with a numerical answer key. Website state, actual file writes, skill discovery and physical devices require their own tests.

The three generated H3 keys were also checked by numerical integration from their stated forces at two sets of physical parameters. The program recovers initial velocity or force amplitude from boundary conditions in the first pair. The final replay's return-at-rest problem produces a repeated root in the position polynomial. For dimensionless time `s=t/T`, position divided by `uT` is `s(s²−λs+1)`. At a nonzero return at rest the quadratic has a double root, giving `λ=2` and `s=1`. Reversals at `1/3` and `1` give a distance of `62uT/27` and a speed-to-velocity ratio of `31/27`. The integrator rejects deliberately substituting signed displacement for total distance. Both reserve circuit prompts specified 4 Ω in series with 6 Ω and 3 Ω in parallel at 12 V. The parallel combination is 2 Ω, so the junction voltage is 4 V, the branch currents are 2/3 A and 4/3 A, and their sum is 2 A. Opening the 3 Ω branch increases current through 6 Ω to 1.2 A.

## Sampling and limits

The published baseline was `1bc3ccf735c440116bb97cc875940630f61828da`. The original [freeze manifest](freeze.json) was recorded at 18:45:28 UTC on 2026-11-12. The targeted [freeze manifest](targeted-freeze.json) was recorded at 18:54:04 UTC. The original criteria and the supplemental anchors are different instruments. Their counts cannot be pooled into an overall pass rate. The baseline field in T1 and T2 means the first repaired candidate. All other baseline files in the main evidence directory are revision 7.

An evaluator separate from the source owner held back case text and criteria. Each tutor worker saw the exact prior learner and tutor messages for its own conversation and the current learner message only. All 72 generated learner-facing replies across 32 synthetic conversations used fresh, ephemeral, read-only CLI contexts with the installed ChatGPT login. We preloaded SKILL.md and every Markdown file directly under references/ with the same procedure for each arm. Turn metrics recorded no executed tool calls. Each grader received only case IDs, the criteria and the case-wise randomized X/Y transcripts. Both grade records for each double-graded comparison were complete before decoding. The receipts can validate packet identity, not prove absence of other access to shared storage.

This evaluates explicit instruction loading with a particular host and its existing model access. The 72 tutor calls reported 3,425,713 input tokens (including 1,052,160 cached) and 17,574 output tokens. These counts include host instructions, preloaded references and replayed history. Seed, temperature, exact backend revision and billing were unavailable. Each scenario has one sample per arm, tutors and judges share a provider, the scripted learner cannot react organically, and some rubrics permitted poor teaching choices. The ten separate grader calls are excluded from the tutor token totals. No actual learner took a test, and the suggested exercise times were not validated with students.

## Reproduce

Run these locally from this directory in a full clone. Use the release commit as `--candidate` if running after later edits, or `WORKTREE` before the release commit. The first command verifies every complete tutor prompt from the appropriate source snapshot and all primary grade packets. The second verifies the tighter development replay against its source snapshots. All checks run offline.

```sh
python -B check.py --broad-replay --repo ../../../../.. --candidate HEAD
python -B replay.py check --repo ../../../../.. --candidate HEAD
python -B verify_mechanics.py
python -B -m unittest discover -s . -p test_evidence.py -v
```

A shallow checkout without the historical commit can run the first two without `--repo` to verify the frozen cases, transcripts, grade identity and counts. Negative tests corrupt copies of the saved inputs, a transcript, the assignment key, the grade coverage, the second grader's prompt digest and a JSON key. The corrupt copies must fail their respective checks.

For new samples use scratch output directories. `evaluate.py run SPLIT OUT REPO REV ARM` reconstructs one side. Add `--overrides development-overlay.json` or `--overrides first-freeze-overlay.json` to read an earlier draft against the final release source. Use published revision 7, the first repair, or final source according to the table above. Run `evaluate.py mask SPLIT OUT`, then `evaluate.py grade SPLIT OUT primary` and, where planned, `second`. For the broad replay use `--reuse-baseline ORIGINAL_OUT` when masking. The supplemental `replay.py` supports `mask`, `grade` and `check` with a scratch `--root` containing the same freeze files and directory layout. Only `run` and `grade` call a model. A new sample or grader may return a different result. All published scenarios are exposed for future versions.

## Real learner trial

Choose two pairs of previously unseen, instructor-checked problems for the same capability. Start with short unaided pretests to identify comparable difficulty. Randomize the revision order within one pair, reverse it in the other, and match time and permitted aids. Capture the first unsupported step, time actually spent and any help. Ask for an immediate unseen variant without help. About a week later, change the representation or constraint and score an unseen solution without revealing the method. Decide on criteria before instruction and have a person blind to condition score the reasoning. Record missed sessions and earlier exposure. Expect large topic and order effects with one learner. The week is a proposed trial interval. Butler's experiments used a week-delayed test with new questions after studying prose passages. That work motivates testing transfer with a separate task, and supplies no estimate for this skill. [Primary study](https://pubmed.ncbi.nlm.nih.gov/20804289/)
