# Release-candidate tutoring comparison

Six tutor sessions answered the same 20 synthetic learner scenarios. Three sessions used the published revision 4 and three used the edited revision 5 candidate. Fifteen scenarios had one learner message. Five supplied a second learner message that followed the tutor's initial answer. This yielded 120 conversations and 150 tutor replies.

| Tutor instructions | PASS | PARTIAL | FAIL | Rubric decisions |
|---|---:|---:|---:|---:|
| Revision 4 | 340 | 20 | 15 | 375 |
| Revision 5 candidate | 351 | 19 | 5 | 375 |

The candidate received a stronger rubric profile in seven cases, a weaker profile in three, identical counts in nine, and a mixed result in one. A stronger profile has at least as many passes and at most as many failures, with one strict difference. The original bounded criteria and all grades are retained in [the cases](cases/). Recompute the counts with `python -B check_results.py`.

On E04, all three candidate tutors supplied an independent check for the binary-search repair. On E07, all three engaged with the induction argument within the length and follow-up-question constraints. E11 had three fully passing candidate storyboards. In E01, two candidate tutors completed the numerical check themselves and earned a failure on leaving a check for the learner. In E05, the candidate had one additional partial rating, and all six tutors led with the requested weakness. The fixed rubric awards a failure for omitting a strength before criticism. That particular score reflects a choice of teaching style. E08 and E15 also had additional partial ratings for the candidate.

## Method

- Each tutor had a separate sampling context, one skill snapshot, the same prompt set and the [synthetic study fixture](fixture.json). Each treated the cases as separate conversations within its assigned batch. The reserved paper was named in project instructions and withheld. The fixture provided no Manim or LaTeX environment. Tutoring was read-only.
- E02 and T3 specify that the 6-ohm resistor stays in the network. Both versions saw the same clarification. T2 specifies a first bending-deflection estimate. T4 tests a learner supplying a confounder to a causal argument. T5 asks for a stability counterexample from a supplied source sentence.
- For every case the six replies were shuffled into slots A–F. Reviewers received the replies and the fixed rubric before the version key was revealed. A separate reviewer rated E04 and T5 independently and agreed with the first ratings on all 66 decisions for those two cases. The [calibration file](calibration.json) includes the second reviewer's reasons.
- One E14 grader initially treated a real fixture journal entry as invented because their briefing omitted the prior hint. The entry records difficulty with an inner derivative and an open question about trigonometric inner functions. All six E14 replies were rechecked while still masked. Two ratings changed for the same reply. The [correction](grading-correction.json) preserves the earlier and corrected ratings.
- Each case includes the exact learner messages, criteria, full tutor replies, reasons and decoded sample key. The two tutoring snapshot manifests identify the entry point and reference file bytes used in the comparison. The host's model and sampling behavior may change across runs.

Each tutor contributed multiple replies and each grader rated multiple criteria. Interpret counts at the case level. The experiment measured simulated replies to an invoked skill. Human learning, delayed retention, and whether either host selects the skill implicitly require separate observations.

## Follow-up

The broad comparison exposed recurring omissions about timing a still frame and profiling idle updaters, and difficulty making the limits of cross-subject transfer explicit. Two corresponding instructions were revised after the broad comparison. A new reviewer graded a shuffled mixture of the three original candidate replies and three fresh replies per case. E12 changed from 10 passes and 8 partials to 18 passes. E15 changed from 16 passes and 2 partials to 17 passes and 1 partial. The broad table retains its original denominators. The release also includes subsequent software safeguards for render output selection and subprocess timeouts. [Targeted replies, keys and reasons](targeted.json)
