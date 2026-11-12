# Technical roadmaps

For exploratory work, an appropriate checkpoint may be a correct visual prediction, a counterexample, or a proposed experiment that distinguishes two models. Preserve the learner's open questions. Do not require every branch to end in an exam score or an engineering deliverable. Use [visual inquiry](visual-inquiry.md) when choosing those checkpoints.

Use this guide to create or revise a learning plan. Start with a concrete capability, such as solving constrained optimization problems unaided or implementing and checking a periodic FPGA timer. An interest in several fields does not require a curriculum covering all of them.

Use [the roadmap template](../assets/roadmap.template.md). Inspect the current course materials, project constraints, and authorized session records before filling it. Keep unknown prerequisites explicit; do not convert an assumed background into a demonstrated skill.

For a new multi-session goal, use the short agreement in [deliberate practice](deliberate-practice.md). The roadmap carries the agreed capability and the evidence for changing the next checkpoint. Revising the goal is a planning decision; it adds no evidence of performance.

## Exchange one observation with the optional roadmap website

The compact skill works in chat and with existing private files. The full source checkout also contains a local browser roadmap and its format guide, `roadmap/FORMAT.md`. The browser cannot discover or update a session file. For a requested export, work in the authorized private location and inspect the observation before copying it.

```sh
python scripts/export_roadmap_event.py SESSION.json --event 1 --skill aliasing --output NEW.json
```

Run the script from the skill folder and supply paths to the authorized session and a **new private output file**. Event numbers start at 1. Use a skill ID that exists in the destination roadmap; `aliasing` is an example. For a legacy event without an attempt ID, add `--id` and keep that opaque identifier for the same observation on subsequent exports. An optional `--session-ref` labels the source without disclosing its filesystem path. Review the derived JSON before importing the event into the browser. Export a single event back to the PPP session format from the website when needed. Reconcile by attempt ID before adding it to an existing journal.

Keep existing Markdown roadmaps and dated sessions in place. Copy verified goals and prerequisites deliberately. Import only observations supported by the authoritative private evidence. A checked resource or a plan written in Markdown supplies no attempt. Correct or delete the private observation and its authorized browser copy separately. An exported backup remains a separate copy. A whole-roadmap restore replaces browser data and requires review. A review date is a planning field.

## Plan from observable work

1. State the target capability and conditions, including allowed tools, assistance, time limits, and physical equipment when relevant.
2. Map only the prerequisites needed for that capability. Separate essential topics from optional extensions and note their dependencies.
3. Choose milestones that produce inspectable work. Examples include an independent derivation, a correct model of an unfamiliar problem, a tested implementation, or a justified design choice.
4. Define each checkpoint's expected result and its source before evaluation. Include a boundary or invalid-method case when it can expose a plausible mistake.
5. Record the observed result and assistance separately. Keep planned work, attempted work, verified artifacts, and untested claims distinct.

For each knowledge point, track four kinds of evidence separately: explain, solve unaided, transfer, and delayed retrieval. [Study habits](study-habits.md) defines them. Describe the evidence in words and link each claim to the dated work and help used. Leave an untested prerequisite open.

Maintain separate tracks for unaided solving and assisted engineering. Successful code produced with AI can support a claim about the implementation and the learner's documented review decisions. It does not establish unaided coding or mathematical competence. Simulation, source review, instrument measurements, and physical-device tests each support different claims.

For a hardware or software project, connect one theory decision to a real implementation tradeoff. For example, before simulating a synchronous counter, predict the value after an enabled rising edge and after a disabled edge. Compare those expectations with the trace and include a reset case under the design's stated reset convention. Record what the learner predicted, what the simulator showed, and which physical measurements remain open. Advance the checkpoint that the observation supports.

## Sources and effort

Use original course material for exam scope and notation. Use primary technical documentation, original research, or trusted reference results for engineering requirements. Record the title, edition or version, relevant section, and locator. An unverified source is a research task, not authority for a checkpoint.

Give effort ranges as estimates with assumptions, such as current prerequisites, available equipment, and weekly time. Leave the estimate unknown when evidence is too weak. Distinguish planned study time from recorded elapsed time. Review an estimate after actual work rather than quietly treating it as a promise.

## Revise from evidence

Use dated session evidence to select the next task. If a checkpoint fails, identify the missing prerequisite or first unsupported step before expanding the plan. If it succeeds with help, retain that assistance in the record and choose an independent check. If it succeeds independently, choose a suitably different problem or a later retrieval check. Do not apply an arbitrary success count as a universal mastery threshold.

Record the reason for each consequential revision. Preserve protected papers and fresh timed attempts. Suggested follow-up dates are planning choices; create a reminder only when requested through an available supported scheduling tool. End with the next concrete task and the evidence needed to choose what follows it.
