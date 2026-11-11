# Revision 6 tutor-response comparison

Revision 6 clarifies essay feedback, engineering approximation decisions, and reasoning moves between subjects. The comparison does **not** establish a broad performance gain. The published baseline already answers these fresh cases well. A small apparent transfer gain depends on whether a worked application satisfies the rubric or a separate learner exercise is required.

The baseline is the actual published revision 5 at `f9b02a07ec97d99477a9e110667879f97a0f1db4`, including its later transfer wording. The [diagnosis](diagnosis.md) distinguishes the broad revision 5 candidate from the wording eventually published, and examines complete E05, E08 and E15 replies, grades and decoded keys. Historical evidence is unchanged.

## Results

Counts below are criterion decisions, not learners or independent conversations. Each area has three fresh cases, three tutor contexts per version and five criteria per conversation, giving 45 decisions per area and version.

| Area | Original issue and change | Primary baseline P / partial / F | Primary candidate P / partial / F | Interpretation and remaining limits |
|---|---|---:|---:|---|
| Essay | E05's extra partial implied a band without an estimate label. Clarify scope and basis of marks; distinguish weakest-point diagnosis from full rubric marking. Preserve requested full paragraphs. | 45 / 0 / 0 | 45 / 0 / 0 | Unchanged. Cases cover an inference repair, all analytic allocations, and useful feedback without criteria followed by an estimated band when descriptors arrive. Human mark calibration is untested. |
| Beam judgment | E08's extra partial names determinants but leaves the next action implicit. Route model adequacy explicitly; compare the relevant omitted contribution with a stated budget, or select the decisive missing input. | 45 / 0 / 0 | 45 / 0 / 0 | Unchanged. All samples change the verdict after the depth correction, use the different central-load coefficient and resolve the missing-depth case. These checks cover stipulated static rectangular beam models, not total hardware error. |
| Cross-subject transfer | Published E15 still has one partial for an implicit disciplinary boundary. Demonstrate one move on supplied work, name destination evidence and offer a short application in either direction. | 43 / 2 / 0 | 45 / 0 / 0 | Stronger under the primary grader's exercise interpretation; both are 45 / 0 / 0 when a worked application counts. No robust advantage follows from this ambiguity. Unaided learner transfer is untested. |

All three controls pass for both versions: immediate complete model paragraph, one-sentence confirmation of a correct attempt, and acceptance of a valid denominator correction. Each version receives 45 / 0 / 0 control decisions.

The primary aggregate is **178 PASS, 2 PARTIAL, 0 FAIL** for the baseline and **180 PASS, 0 PARTIAL, 0 FAIL** for the candidate. With the consistent clarification below, both become **180 / 0 / 0**. Five development contexts per version produced 30 replies and 150 PASS decisions, with no partials or failures. No instruction repair was made from a held-out result.

## The rubric ambiguity and independent review

The primary grader gave X3 slots A and B a PARTIAL on `area_requirement`: neither adds a separate learner exercise. Their `next_action` grades pass because the replies give concrete repairs or checks. Both replies demonstrate the requested move on the actual sentence, discuss historical evidence, and give a supported rewritten claim. X3 asks for an example. Its area criterion says "offers one small application"; the general criterion permits a completed direct answer without another task.

Before decoding the labels, an additional fresh blinded reviewer assessed all six X3 replies. The reviewer concluded that a worked application satisfies the wording and reconciles it with the learner's request. All six pass under that interpretation. The alternative requiring a separate exercise reproduces the original two partials. After every review completed, the key identified A and B as baseline samples 3 and 2. The [original case](heldout/X3.json), [exact extra packet](rubric-review/packet.json), [original assessment](rubric-review/assessment.json) and [clarification](rubric-review.json) retain both readings. The primary grades were not replaced.

A second blinded grader independently assessed the preselected A3, B1, X1 and C3 sample: 24 conversations and 120 decisions, all PASS and no rating disagreements with the primary graders. That sample was selected before tutor generation. The additional X3 review was prompted by a rubric issue and is reported separately. These model reviews are supplementary judgment, not human evaluation.

## Method and frozen inputs

- [Protocol](protocol.json), [held-out cases and criteria](heldout.json), [development cases](development.json), [fixture](fixture.json), [reference calculations](beam_reference.json) and their [SHA-256 freeze](freeze.json) were fixed before new tutor generation. The improvement rule requires passes to stay the same or rise, failures to stay the same or fall, one strict difference, and no increase in correctness or help-level failures. Equal profiles remain unchanged.
- Each tutor context used only one neutral instruction snapshot, the same fixture and messages, and relevant routed references. The [instruction manifest](instruction-manifest.json) records exact source hashes. All contexts inherited the same parent model without overrides. Seed and temperature controls were unavailable. Five development contexts per version preceded three fresh held-out contexts per version.
- Every tutor-read instruction file matches the published source hashes. Two unused measurement JSON files in the candidate snapshot had CRLF line endings while their unchanged Git blobs use LF. The [byte-equivalence record](snapshot-byte-equivalence.json) preserves both hashes and the reversible reconstruction. The original sampling manifest remains unchanged; no tutor read either measurement file.
- The six held-out contexts produced **72 conversations and 96 tutor replies**. Four cases supply fixed follow-up messages. Those messages were visible in each batch and processed in sequence after the preceding answer. This does not establish the same behavior with an unexpected live follow-up. Cases were treated as distinct conversations within a context; observations sharing a context are correlated.
- Replies were independently shuffled into A-F labels for each held-out case, and A-J for development. Primary graders received the fixture facts and only masked packets. The second reviewer received the same exact replies in the selected cases. The version key remained separate until grading and the ambiguity review completed. Retained files can demonstrate text identity, but cannot alone prove chronology or access isolation.
- Permissions and source access were identical and limited by instruction, with no operating-system isolation. Action metadata are tutor reports of the sources and commands used; shared reads may serve several cases. Private routing roots and snapshot names were removed from action metadata before grading. Learner-facing reply strings were not edited. The [packets](packets/heldout/essay.json) retain the exact content shown to graders, and each [case](heldout/A1.json) retains its decoded key and reasons.

## Mathematics and rejection checks

The beam reference integrates `M*m/(EI)` and `V*v/(kappa GA)` independently of tutor output. For B1, omitted shear is 4.6484% of total initially and 0.1946% after the depth correction, so the 2% verdict must change. B2's simply supported central load yields 3.0933%, meeting its 4% shear budget. B3's unknown depth interval straddles a threshold of approximately 91.04 mm, making bending depth the decisive measurement. Source assumptions and limits are recorded in the reference and [provenance](../../../../../references/provenance.md).

The checker uses exact rational polynomial integration against independently frozen decimal expectations. Controlled faults demonstrate rejection of a wrong percentage denominator, a cantilever coefficient substituted for the simply supported coefficient, changed frozen input, changed grader reply, missing grades and duplicate version mappings. Validator tests also preserve original totals when computing the separate rubric sensitivity. Structure and arithmetic checks do not decide whether a reply is good tutoring.

Run from this directory:

```sh
python -B check_results.py
python -B -m unittest discover -s . -p 'test_evidence.py' -v
```

The first command reproduces the raw totals, per-area comparisons, non-PASS reasons, second-review disagreements and the separately labelled rubric sensitivity. The second runs 33 requirements-based and corruption tests. [Saved report](summary.json)

The repository's existing unit tests, historical evidence checks and starter model checks also remain applicable. The workflow runs the new checker and its negative cases on Python 3.9 and 3.12. A scoped Git attribute preserves the frozen evidence bytes while retaining the repository's default LF policy; an isolated staging/checkout experiment rejected the unprotected conversion.

## One practical illustration

Historical E08 revision 5 sample 2 ends by saying that section, load, quantity and allowed error determine adequacy, without an explicit next action. A [single first-sample replay](historical-replay.json) of the same learner message under revision 6 ends: "What loading is applied to your cantilever?" It explains the short-beam shear concern while distinguishing a pure end couple from a transverse load. This illustration is excluded from all comparison totals. It shows a concrete next question, not a reliability estimate or a measured learning gain.

No real learner participated. These tests establish neither delayed retention nor examination performance, grade calibration, real engineering adequacy, implicit skill triggering, or successful unaided transfer. The supported release claim is narrower: explicit guidance and reproducible evidence, with no regression detected in these cases and no broad improvement demonstrated.
