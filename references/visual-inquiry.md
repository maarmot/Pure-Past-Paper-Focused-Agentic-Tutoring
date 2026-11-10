# Visual inquiry

Use this path when the learner wants to see a difficult idea, investigate a question, or explore a connection. A failed exam question is not a prerequisite. Keep exam repair available, but do not turn every exploration into a timed assessment.

## Start from something worth investigating

Find the representational obstacle: what is hard to imagine, distinguish, connect, or infer? A difficult formula is not automatically a difficult visual idea. Useful obstacles include different worlds producing the same measurements, local change hiding global behavior, and a familiar diagram suppressing a physical assumption.

Begin with a concrete situation and an honest question. Let the learner predict, sketch a candidate, change a control, or ask their own question before revealing a prepared explanation. Accept "show me" as a valid request. Do not manufacture suspense or withhold a requested answer.

Keep the phenomenon visible while explaining it. Introduce notation when it names a relationship the learner can inspect or when they request the derivation. Equations, definitions, and proof remain available in a separate layer; a convincing picture cannot establish a universal claim.

Use [the inquiry storyboard](../assets/inquiry-storyboard.template.md) to prepare consequential changes and checks. It is a planning aid, not a compulsory sequence or fixed number of scenes.

## Let the question change

Follow a useful learner question even when it departs from the prepared example. State what the new question changes, bookmark the original question and current state, and keep unrelated parameters fixed. Offer a way back without forcing a return. A surprising observation may justify a second candidate model or a different measurement.

Give controls names that describe their effect. Distinguish changing the physical system, changing the measuring instrument, changing a model assumption, and merely changing the camera or axis scale. Reset should restore a documented starting state. Reveal should be optional, clear, and reversible where useful.

An inquiry can end with a supported explanation, a discriminating observation, a counterexample, or a precise unresolved question. Ask what the learner would investigate next and why. Return to exam practice when it serves their goal; do not require it as payment for exploring.

## Choose a concept with an actual visual obstacle

These are candidate designs, not claims that all topics have been implemented or that a technique improves learning.

| Concept and visual action | Tempting misconception | Counterexample or discriminating check | Conditions and limits |
|---|---|---|---|
| Sampling ambiguity: reveal two continuous motions beneath the same measured dots; change only the sampling times. | A smooth curve through the observations is the uniquely measured motion. | The fixed 1 Hz and 11 Hz circular motions below agree at 10 samples/s; an added observation at 0.05 s separates them. | Specify whether the observation is full position or one coordinate, plus phase, timing, and noise assumptions. Distinguishing two candidates does not uniquely reconstruct arbitrary motion. [Sampling reference](https://visionbook.mit.edu/sampling_and_aliasing.html). |
| Gradients and conditioning: compare contour maps and descent paths while identifying axis scales, coordinate units, metric, and step rule. | The steepest-looking screen direction determines the physical gradient; rescaling a drawing automatically fixes an algorithm. | Change display aspect ratio without changing the objective or algorithm: the data-space path must remain unchanged. Treat a coordinate change or preconditioner as a separate experiment. | State the norm and update rule. Coordinate scaling can change conditioning; this is not a universal speed guarantee. [Boyd and Vandenberghe, chapter 9](https://www.seas.ucla.edu/~vandenbe/cvxbook/bv_cvxbook.pdf). |
| Transient growth: show a state trajectory and its length together, with an eventual-decay view available. | Negative-real-part eigenvalues mean every disturbance immediately shrinks. | For x′=Ax, A=[−1,10;0,−2], x(0)=(0,1), the exact state at t=ln 2 is (2.5,0.25). Its Euclidean norm exceeds its initial value 1, although it eventually decays. | Declare the Euclidean norm and linear time-invariant model. Asymptotic stability and monotonic decay are different claims. Re-derive the stated solution independently. [Nonnormality reference](https://www.cs.ox.ac.uk/pseudospectra/). |
| Fourier locality and phase: translate a localized feature while showing the corresponding phase changes and unchanged spectral magnitudes. | A frequency coefficient is one local piece of the shape, or magnitude alone determines where a feature occurs. | A time shift changes Fourier phase while preserving magnitude. Compare the original and shifted feature before displaying the transform rule. | Specify transform convention, finite window, periodicity, and approximation. Do not mistake a truncated reconstruction for an exact arbitrary signal. [MIT Fourier properties](https://ocw.mit.edu/courses/res-6-007-signals-and-systems-spring-2011/resources/lecture-9-fourier-transform-properties/). |
| Metastability: place an illustrative analog voltage trace beside the clocked logic view; vary asynchronous arrival relative to the capture edge. | A digital schematic's 0/1 wires describe all physical states; two registers guarantee that uncertainty vanishes. | Show why extra settling time can reduce propagation risk without asserting zero risk. Label every illustrative voltage trace as schematic. | An animation or ordinary digital simulation is not a device measurement or a calibrated failure-rate prediction. Device parameters and implementation timing matter. [Altera metastability guidance](https://resources.altera.com/quartushelp/17.1/analyze/sta/sta_com_report_metastability.htm). |

## Worked design: the same samples, different motion

Hold both candidate worlds fixed. They are points moving around a unit circle at 1 and 11 turns per second, both starting at (1,0). Radius and position coordinates are dimensionless; time is in seconds. The measurement is the full two-dimensional position. Let the learner change sampling frequency or add one measurement. Do not change a world's frequency automatically when the sampling control moves.

At 10 samples/s the dots agree. Invite a proposed connection between them, then reveal both compatible motions. Ask what observation would distinguish these candidates. A learner may choose another sampling rate, an extra timestamp, or a different measured quantity; evaluate their actual proposal.

After the visual experiment, offer the [optional mathematical certificate](aliasing-certificate.md) if the learner wants the derivation. Its key checks use p_f(t)=(cos(2πft), sin(2πft)):

- At t=n/10, the angles differ by 2πn for integer n, so both measured positions agree.
- At t=0.05, the angles are π/10 and 11π/10. The positions are opposite vectors, with Euclidean distance 2.
- At 12 samples/s, the positions are (cos(πn/6), sin(πn/6)) and (cos(πn/6), −sin(πn/6)). They differ except at n divisible by 6. At t=1/12 they are (√3/2, +1/2) and (√3/2, −1/2), with Euclidean distance 1.

What the instrument measures is consequential. If it records only horizontal position, these candidates remain indistinguishable on the 12 samples/s grid because their cosine coordinates agree. A useful optional branch is "Would this experiment still distinguish them if the camera could see only one coordinate?" Keep that change separate from changing the sampling rate.

Before release, check these values independently of the animation helper. Verify that changing sampling leaves both motions fixed; every sample lies on its candidate curve; the extra measurement is at its labeled time; and reset restores the starting reveal/control state. At 12 samples/s, claim only that these two specified candidates can be distinguished. It does not satisfy a blanket reconstruction condition for every signal containing 11 Hz.

Useful open questions include "Which other motions still fit these dots?", "What assumption would make reconstruction defensible?", and "Would this extra sample still help if the measurement were noisy?" Use the learner's question when they have one. Do not equate an unanswered question with failure or a displayed prompt with demonstrated curiosity.

## Evidence of what happened

Keep the learner's actual prediction, question, observation, explanation, and requested next investigation distinct from the tutor's interpretation. Record assistance and unresolved checks. A learner who changes an explanation after a counterexample has supplied useful evidence, but not proof of durable understanding. If no learner has used the activity, report only its mathematical, interaction, and media checks.
