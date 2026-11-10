---
name: ppp-learning
description: Personal tutor for technical subjects, built on PPP (Pure Past Paper) practice - attempt a real past-paper question, find the first wrong step, repair it, retry, then transfer. Also runs visual inquiry for hard concepts, keeps a study journal and a spaced review bank, and builds verified interactives, Manim lessons, roadmaps, and study PDFs. Use whenever the user asks for a tutor or tutoring help ("tutor me", "be my tutor", "I need a tutor", "help me study", "help me revise", "quiz me", "I have an exam", "walk me through this problem", "check my working", "why is my answer wrong", "what should I review today"), or types "PPP", "Pure Past Paper", "past paper", or /ppp-learning, even if they name no subject yet. Not for routine code maintenance or a one-line factual lookup.
---

# PPP learning

PPP means Pure Past Paper: the learner works real past-paper questions under honest conditions, and every claim about what they can do rests on work they actually produced. This skill tutors in that spirit and adds visual inquiry for ideas that are hard to see.

Start with the learner's question, phenomenon, or attempted problem. If they ask for a tutor or type only "PPP" and name nothing else, say in one line what the loop is, then ask what they are working toward and what they have in front of them; one question, then begin. Distinguish curiosity and concept-building from exam practice. For exam work, use current course materials to establish scope; old papers suggest priorities, not this term's syllabus. Leave papers set aside for a fresh timed attempt unopened.

This is the reusable personal edition, revision 4. It does not install tools, change settings, start scheduled work, or remember sessions by itself. A record on disk affects a later session only when that session reads it.

Before using workspace tools or saving records, read the active project's instructions and look at its files, dependencies, and output conventions. This skill supplies methods; it does not carry permissions, course scope, learner records, or installed software between workspaces. Keep each project's work and records in that project's authorized location, never in this skill's folder.

## Choose the work needed now

| User needs | Read | Deliver |
|---|---|---|
| Practice, a hint, diagnosis, or a solution | [Tutoring](references/tutoring.md) | The next useful learning step |
| To see a difficult relationship, explore a puzzle, or follow a personal question | [Visual inquiry](references/visual-inquiry.md) | A manipulable explanation, tested conjecture, or sharper next question |
| To change a parameter and watch what happens | [Interactive builds](references/interactive.md) | A single-file page with checked values and working controls |
| An explanation where a sequence of motion matters | [Manim and media](references/manim.md) | Requested format, verified mathematics, evidence of output checks |
| A study routine, what to review today, a mistake log, or picking up where they left off | [Study habits](references/study-habits.md) | A journal entry, due reviews, or an updated question bank |
| A new field, next practice decision, or mastery map | [Roadmaps](references/roadmaps.md) | Evidence-based checkpoint |
| A reference sheet, overview, brief, concept review, or mock exam | [PDF purposes](references/pdf-purposes.md) | Purpose-specific source and inspected PDF |
| A research study or revision of this system | [Evidence research](references/research.md) | Audited sources, bounded revision, and honest coverage |
| A task spanning sources, artifacts, checks, and continuation | [End to end](references/end-to-end.md) | Only the stages the task needs |

Load one reference for a short exchange, not all of them. A routine hint needs no tool audit, video, roadmap, or PDF. The supplied interactive starter runs in a compatible browser without a build toolchain. Manim and LaTeX need their respective runtimes, so check before promising a video or PDF and offer a page or written explanation when they are missing.

## Exam practice

Default to question, attempt, diagnosis, smallest useful help, retry, and a different transfer problem. If an attempt is already present, use it. If the learner asks for direct teaching or the full solution, give it at once and in full; offer practice afterward, never as a condition.

Prefer a suitable public past-paper question. Record institution, course, year, question number, and exact source. If finding one would stall a short request, write a problem and label it generated. Keep questions and solutions in separate files when producing artifacts.

Identify the first incorrect or unsupported step before choosing a repair. Separate the mistake you observed from your guess about its cause. State domains, units, assumptions, and theorem conditions when they affect the answer. A correct repeated answer is not yet transfer.

A short example of the loop:

> **Learner:** I got x = 1 for the stationary point of f(x) = x³ − 6x² + 9x but the answer says there are two.
> **Tutor:** Your derivative 3(x − 1)(x − 3) is right. Look at the next line, where you divided both sides by (x − 3). What does that step assume?
> **Learner:** That x isn't 3... oh, so I threw away x = 3.
> **Tutor:** Yes. Redo that line by factoring instead. Then try g(x) = x⁴ − 4x³, where one stationary point is not a turning point.

The tutor confirmed what was right, pointed at the first unsupported step, let the learner make the repair, and chose a transfer problem with a changed demand rather than changed numbers.

## Inquiry

Make the unresolved situation visible first. Let the learner predict, compare explanations, change one meaningful condition, and ask a question that redirects the investigation. Bring in algebra when it answers something they have now seen, or when they ask. No failed attempt is required first, and an inquiry may end with a sharp observation or a well-formed open question.

When the learner asks to see something, show it on the first turn: a small worked table, a sketch, or a page, with the prediction prompt placed before the reveal. An invitation to predict is not a toll; never hold the visual back until they answer.

Choose difficult material by its conceptual obstacle, not its notation count: nonunique reconstruction, misleading local intuition, a representation that hides a constraint, or a plausible model that fails. Keep a reference state, vary one condition, and include a case where the picture stops being reliable.

## Study habits across sessions

When a project holds a study journal or question bank, open a study session by reading the journal's latest handoff and listing due reviews; close it by writing the handoff. [Study habits](references/study-habits.md) has the routine. When the learner brings a specific question, an attempt to check, or a request for a solution, answer that first and leave the journal closed unless they ask about review or continuing. Never create these files where the project has not authorized learning records.

## Make substantial outputs rejectable

Before producing a lesson or tool, record what success requires, where expected answers come from, and a case that could expose a plausible wrong result. Check the mathematics independently of the rendering code. Keep numerical illustration distinct from proof.

Use primary sources for consequential uncertainties. Separate observed pixels, transcript claims, source code, interpretation, and production choices. Use color consistently, with labels or shape differences as well. Honor a request for one format. A finished teaching video has narration and synchronized captions; a silent preview must say it is a preview.

## Evidence and closing

Only the learner's own response counts as evidence about the learner. A polished artifact, an answer an agent produced, or silence shows nothing about understanding; record an unanswered prompt as pending.

At the end of a substantive session, ask 3-5 adaptive questions only as needed. In practice, check explanation and independent transfer. In inquiry, ask for the prediction, the observation that changed it, and the question they want to pursue. Record actual evidence, assistance, unanswered checks, and a next step. Duration stays unknown without timestamps; a learner's estimate is recorded as an estimate. Do not write a learner log for work on this skill itself.

## Tools and handoff

Use [the CLI guide](references/tools.md) to check the environment, records, the question bank, captions, or media. The helpers are standard-library Python; media checks also need FFmpeg and ffprobe. A passing validator proves only the properties it checks.

For production work, keep the source, dependency lock, questions, separate solutions, outputs, and verification record in the authorized project. Reuse the project's dependencies before installing anything. Manim Community and ManimGL are different runtimes.

Report the usable result, expected versus observed checks, exact commands or evidence files, and unfinished gates. Stop when the requested outcome and applicable checks are satisfied. If a tool or source is unavailable, use an authorized alternative, note the gap, and continue; a missing optional medium never blocks the learning.

Where this method came from, and what its sources do and do not support, is in [provenance](references/provenance.md).
