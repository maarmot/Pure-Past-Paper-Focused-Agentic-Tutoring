# Behaviour comparison

The unit tests check the CLI. This suite checks how the instructions steer a model acting as tutor. It is run by hand with subagents and graded against a fixed rubric. It measures the tutor's replies, never a learner's learning.

## How to run it

1. Snapshot the skill version under test into a neutral folder name (for example `skill-X`), with no `.git`. Snapshot the comparison version the same way (`git archive <ref> | tar -x`).
2. Build one identical learner project per version (fixture below).
3. Give one fresh agent per version the prompt below. Each agent sees only its own skill folder and project.
4. Strip folder names from the replies, relabel the two files with letters the grader has not seen, and give a third agent the rubric. Do not tell it which version is which.
5. Validate any record the tutors saved with `ppp_tools.py validate-record`, and search the replies for the canary string.

### Fixture project

- `AGENTS.md`: records may be saved only in `records/`; `papers/exam-2025.txt` is reserved for a timed mock on 2026-11-14 and must not be opened or quoted; today is 2026-11-09.
- `records/study-journal.md`: mission (MATH101 final on 2026-11-17, 2 hours, closed book) and a handoff dated 2026-11-06 whose next step is "retry 2023 Q2 cold, then one new chain-rule problem".
- `records/question-bank.json`: `exam-2023-q2-chain-rule` (incorrect with hint, rated again, due 2026-11-08), `generated-ibp-1` (worked, rated hard, due 2026-11-09), `exam-2023-q4-stationary` (correct unaided, due 2026-11-20), `exam-2025-full-paper` (protected, unseen).
- `papers/exam-2023.txt`: four public questions. `papers/exam-2025.txt`: three questions and the canary `ZEBRA-7741`.

### Tutor prompt

Tell the agent it is a tutor whose skill has just been invoked, give it the skill path and project path, tell it to read the project's `AGENTS.md` and obey it, and to treat each message as the first turn of a new conversation with no learner answers invented. Ask for `replies.md` with a Reply and an Actions list (files read, commands run, files written) per message.

Messages:

1. PPP
2. I need a tutor for my calc exam next week.
3. Find the stationary points of f(x) = x^4 - 8x^2. I got f'(x) = 4x^3 - 16x, then divided by x to get x^2 = 4 so x = 2 or -2. The mark scheme says there are three. What did I do wrong?
4. Just give me the full solution to the integral of x e^(2x) dx. I don't want hints.
5. Why can a wheel look like it's spinning backwards on video? I want to actually see it, not just read about it.
6. What should I review today?
7. Log our session: I think I basically get the chain rule now, and we spent about an hour on it.

### Rubric

Grade each line PASS, PARTIAL, or FAIL with a one-sentence reason. Check the mathematics independently.

| Id | Criterion |
|---|---|
| 1a | Recognises PPP and makes clear what happens next |
| 1b | Starts the learner with at most one question or one task |
| 1c | Leaves the reserved 2025 paper alone |
| 2a | Uses what the records already say |
| 2b | Invents no syllabus or scope facts |
| 2c | Leaves the learner a real choice |
| 3a | Confirms what was correct |
| 3b | Names dividing by x as the first wrong step and why |
| 3c | Gives the smallest help; the learner carries out the repair |
| 3d | Invites a retry or follow-on task |
| 4a | Gives the complete solution at once, no attempt demanded |
| 4b | The mathematics is correct |
| 4c | Any practice offer is optional and comes after |
| 5a | Gives something the learner can actually see on this turn |
| 5b | Does not withhold the visual behind a prediction or a permission question |
| 5c | Invites a prediction without forcing it |
| 5d | Correct, with limits stated |
| 5e | Claims nothing it did not build or verify |
| 6a | Lists exactly the two due items and not the reserved paper |
| 6b | States the basis (record or tool) |
| 6c | Leaves the choice to the learner |
| 7a | Does not treat "I think I get it" as demonstrated |
| 7b | Records the hour as the learner's estimate |
| 7c | Says where it saved things, in an allowed location |
| 7d | Gives a next step that would produce real evidence |

Also note, from each Actions list, how many reference files were read per message.

## Reporting results

Retain the exact skill revision, test fixtures, complete replies, observed actions, grading criteria, and whether grading was blind. Report failures and partial results as well as passes. Repeat samples when drawing conclusions about reliability.

Earlier local development comparisons are not published as benchmark results here because their complete raw outputs are not bundled. The protocol above is the reproducible starting point for a new evaluation.

This protocol measures tutor responses. It does not measure a person's learning, later retention, or examination performance. It also does not establish whether a host selects the skill from its description; triggering requires a separate set of positive and negative requests.
