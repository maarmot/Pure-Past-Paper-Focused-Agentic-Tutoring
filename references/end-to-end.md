# From a question to a usable learning result

Use this reference when a request spans exploration, research, artifact production, verification, and a learning handoff. A short hint or factual question does not need the whole workflow. The learner's current request sets the scope and degree of help.

## Establish the next useful capability

Start with the learner's question, phenomenon, or existing attempt. Choose [visual inquiry](visual-inquiry.md) for concept-building and personal questions, or [practice and coaching](tutoring.md) for an attempted problem or exam preparation. Reuse what the learner already supplied. Provide direct instruction or a full solution immediately when requested.

State an observable target: explain why two motions fit the same samples, predict a changed case, set up an unfamiliar constraint, or test a technical model. Check only prerequisites that affect the next step. In exam work, inspect current course scope and protect fresh papers. In inquiry, a failed exam attempt is not an entry requirement, and a well-supported open question can be a useful outcome.

Load relevant sources and the latest matching project record if one exists; where the project keeps a journal or question bank, open with [the study-habits routine](study-habits.md). Treat an old record as dated evidence, not proof of current ability. Separate an actual learner statement from an inference about their understanding. If evidence is missing, keep that gap explicit and continue work that does not depend on it.

## Choose an investigation and output

Identify what is hard to see or decide. Choose one useful intervention, such as changing a measurement rate, comparing two candidate models, testing a boundary, or finding a counterexample. Name what remains fixed and what changes. Let a learner question redirect the investigation; preserve the original question and state so it remains possible to return.

Generate only the questions, examples, or variants needed for the current obstacle. Check each before treating it as a trusted exercise or answer key. Label generated and adapted material accurately. Prefer a suitable public past-paper problem for exam practice when available; do not delay a small request indefinitely to find one.

Choose the format by its explanatory job:

| Need | Useful output and route |
|---|---|
| Explain one relationship or repair a small step | A concise explanation or annotated still |
| Let the learner compare cases or test a conjecture | A user-controlled interactive view; use [interactive builds](interactive.md) |
| Explain a consequential sequence of changes | An original narrated, captioned animation; use [Manim and media](manim.md) |
| Preserve a derivation, reference, or practice set | A purpose-specific document; use [PDF purposes](pdf-purposes.md) |
| Resolve a consequential uncertainty | A bounded primary-source investigation; use [evidence research](research.md) |

Use both interaction and video when their roles complement each other and fit the request. Honor a requested single format. Keep equations available as an explanatory or formal layer rather than making them the automatic entry point to a visual inquiry. Use generative imagery for appropriate illustrative assets; exact diagrams, plots, and quantitative motion need reproducible geometry.

## Divide work without replacing the learner

When independent tasks would improve the result, use the host's available collaboration tools. These are task assignments, not assumed registered agents or model names:

- A researcher locates primary evidence, records provenance, and seeks a contradictory case.
- A visual builder implements the chosen representation and meaningful controls from explicit requirements.
- A mathematical skeptic derives expected results independently and checks domains, units, conditions, and counterexamples.
- A reviewer examines actual outputs and reports what the artifact establishes and what remains untested.

Give each worker a bounded question, permitted files or read-only scope, and a concrete deliverable. Keep writers on separate files. Share assumptions needed for the task, but do not give an independent checker the desired conclusion as evidence. Use the current model and delegation rules; if delegation is unavailable, work sequentially and identify the loss of independent review.

The main agent resolves disagreements against sources or runtime observations, integrates the work, and inspects the result. Agreement among agents is not ground truth. No agent may supply the learner's prediction, attempt, or transfer response and then count it as learner evidence. Keep answers and solution files out of an intended independent attempt unless the learner asks for them.

## Build and reject plausible wrong results

Before evaluating an artifact, record expected results and their independent source. Include a case that could expose a tempting wrong model or misleading picture. Keep acceptance criteria fixed during the comparison; explain any correction to them.

Build the smallest complete version that answers the question, then refine actual defects. Reuse the active project's tools and isolated dependencies. Preserve source, parameters, dependencies, and evidence using that project's established output conventions. Do not assume an `output/` or `visual-lessons/` directory exists. Do not render into the installed skill's assets or another workspace.

Check the actual delivered representation, not just a helper function. Compare displayed geometry and values to an independent derivation. For interaction, exercise controls, keyboard use, reset, reveal, and the intended viewport/theme combinations. For video, inspect key frames, decode the finished file, listen to narration, and check captions in playback. For documents, compile and inspect every page. Use [the verification CLI](tools.md) for the properties it can check; it does not replace perceptual review or mathematical reasoning.

Where feasible, introduce a controlled fault in an isolated copy and confirm the check rejects it. Preserve the distinction between a correct model, working code, readable media, and demonstrated understanding. If an optional tool fails, use a suitable authorized alternative and retain the unrun check. Do not call an incomplete gate passed or block all useful learning on an optional medium.

## Return control to the learner

Present the useful result and invite the action that fits the goal: predict, manipulate, explain, propose a distinguishing observation, or solve a new problem. The learner may ask to see the answer or pursue another question instead. Do not impose a transfer test as payment for exploration.

Wait for the learner's actual response before evaluating it. A polished artifact, an answer generated by an agent, or silence supplies no evidence of understanding. Record an unanswered prompt as pending. When feedback is available, identify what it supports and choose the next explanation or question from that evidence rather than following a fixed batch.

## Preserve an honest handoff

Determine whether the current request or active project instructions authorize saving learning records, and where. If so, use a dated, topic-specific session filename and a stable topic roadmap in that location. Otherwise provide an in-chat handoff; ask about persistence only if it matters to the requested task. Respect a request not to log. PPP Method authorizes `learning-system/records/sessions/` and `learning-system/records/roadmaps/` through its own project instructions; that permission does not carry into other workspaces. Do not write account memory or unrelated storage.

Use [the inquiry-session template](../assets/inquiry-session.template.json) for exploration or [the session template](../assets/session.template.json) for practice. Replace template text and dates before saving a real record; the validator rejects leftover starter text. Keep actual learner questions, predictions, observations, assistance, and unresolved questions distinct from tutor proposals and technical verification. Record duration as unknown unless measured timestamps or a labeled learner estimate support it. Installing or building a tool is not itself a learner session.

Update [the roadmap](roadmaps.md) only from supported evidence. Leave untested checkpoints untested. State one concrete next step and the record that a later session should load. A file persists on disk, but its contents influence a future session only when that session reads it.

Close with the usable artifact, what was checked, material uncertainty, and the next learning action. Do not start scheduled reviews, background loops, or future jobs merely because a roadmap recommends them. End-to-end completion concerns the authorized task; learning claims await the learner's own evidence.
